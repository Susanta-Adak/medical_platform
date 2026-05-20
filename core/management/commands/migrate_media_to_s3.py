"""
Management command to migrate all existing local media files to S3.
Run once after fixing S3 settings to move accumulated files off EC2 disk.

Usage:
    python manage.py migrate_media_to_s3
    python manage.py migrate_media_to_s3 --dry-run     # preview only
    python manage.py migrate_media_to_s3 --delete-local # delete after upload
"""

import os
import boto3
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Migrates all local media files to S3 and optionally deletes local copies.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be uploaded without actually uploading.',
        )
        parser.add_argument(
            '--delete-local',
            action='store_true',
            help='Delete local files after successful upload to S3.',
        )
        parser.add_argument(
            '--folder',
            type=str,
            default='',
            help='Only migrate files under this subfolder (e.g. screening_attachments).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete_local = options['delete_local']
        folder_filter = options['folder']

        media_root = Path(settings.MEDIA_ROOT)
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        region = getattr(settings, 'AWS_S3_REGION_NAME', 'ap-south-1')

        if not bucket:
            self.stderr.write(self.style.ERROR('AWS_STORAGE_BUCKET_NAME is not set in settings.'))
            return

        if not getattr(settings, 'AWS_ACCESS_KEY_ID', None):
            self.stderr.write(self.style.ERROR('AWS_ACCESS_KEY_ID is not set. Check your .env file.'))
            return

        self.stdout.write(self.style.NOTICE(f'Scanning media root: {media_root}'))
        self.stdout.write(self.style.NOTICE(f'Target S3 bucket: {bucket} ({region})'))
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no files will be uploaded or deleted.'))

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=region,
        )

        search_root = media_root / folder_filter if folder_filter else media_root
        all_files = list(search_root.rglob('*'))
        files = [f for f in all_files if f.is_file()]

        self.stdout.write(f'Found {len(files)} file(s) to process.\n')

        uploaded = 0
        skipped = 0
        failed = 0
        freed_bytes = 0

        for local_path in files:
            # Compute the S3 key relative to media root
            s3_key = str(local_path.relative_to(media_root))
            file_size = local_path.stat().st_size

            self.stdout.write(f'  → {s3_key} ({file_size / 1024:.1f} KB)', ending=' ')

            if dry_run:
                self.stdout.write(self.style.WARNING('[DRY RUN]'))
                skipped += 1
                continue

            try:
                # Check if already exists in S3
                try:
                    s3.head_object(Bucket=bucket, Key=s3_key)
                    self.stdout.write(self.style.WARNING('[ALREADY IN S3 - SKIPPED]'))
                    skipped += 1
                    # Still delete local if requested
                    if delete_local:
                        local_path.unlink()
                        freed_bytes += file_size
                    continue
                except s3.exceptions.ClientError:
                    pass  # Not in S3 yet, proceed with upload

                # Upload to S3
                s3.upload_file(
                    str(local_path),
                    bucket,
                    s3_key,
                    ExtraArgs={'ContentType': _guess_content_type(local_path.name)},
                )
                self.stdout.write(self.style.SUCCESS('[UPLOADED]'))
                uploaded += 1

                # Delete local copy if requested
                if delete_local:
                    local_path.unlink()
                    freed_bytes += file_size

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[FAILED: {e}]'))
                failed += 1

        # Clean up empty directories
        if delete_local and not dry_run:
            for dirpath in sorted(search_root.rglob('*'), reverse=True):
                if dirpath.is_dir():
                    try:
                        dirpath.rmdir()  # Only removes if empty
                    except OSError:
                        pass

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Uploaded : {uploaded}'))
        self.stdout.write(self.style.WARNING(f'Skipped  : {skipped}'))
        self.stdout.write(self.style.ERROR(f'Failed   : {failed}'))
        if delete_local and not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'Freed    : {freed_bytes / (1024*1024):.1f} MB from EC2 disk'
            ))


def _guess_content_type(filename):
    import mimetypes
    ct, _ = mimetypes.guess_type(filename)
    return ct or 'application/octet-stream'
