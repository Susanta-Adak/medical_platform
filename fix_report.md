# Image Display Fix Applied

1. **Frontend Request Modification:** Updated the `saveQuestionnaire` frontend logic within `questionnaire_builder.html` to stop sending empty stringified File metadata using `JSON.stringify`. Now, it constructs a proper `multipart/form-data` request with the JSON data wrapped inside a form object along with binary image data. 
2. **Backend Payload Readability Updated:** Updated the backend API handlers in `views_builder.py` (`save_questionnaire_api` and `edit_questionnaire_builder`) to correctly parse the JSON out of `request.POST.get('data')` and grab all image files from `request.FILES`.
3. **Renderer Support Addressed:** Refactored `simple_screening_form.html` and verified `simple_questionnaire_display.html` template structures so that `option.option_image` is checked natively for "Custom picture" questions via the frontend.

**To Test Your Fix:**
You can now try it!
Because prior images weren't actually saved in the backend storage, you will need to open the **Questionnaire Builder**, edit your old "Picture test" questionnaire, re-select those images into those options, and finally choose "Update/Save Questionnaire" again. The options should now successfully register and appear properly when you run the questionnaire!
