### Workflow for the Application

1. **User Input**  
   - The user enters a topic.  
   - A script is generated based on the entered topic.

2. **Translation**  
   - The frontend translates the script into Hindi.  
   - Both English and Hindi versions of the script are displayed to the user.

3. **Video Configuration**  
   - The user selects video configurations.  
   - The selected configurations are saved to local storage.

4. **Prompt Generation**  
   - The English script is sent to the backend model for prompt generation.  
   - Prompts are displayed on the screen.

5. **Image Generation**  
   - Prompts are sent to the backend for image generation.  
   - The backend generates images and returns their URLs.  
   - The frontend displays images using the received URLs.

6. **Audio Generation**  
   - On the next screen, the selected language (English or Hindi) is checked.  
   - Based on the language, a list of texts is sent to the backend for audio generation.  
   - The backend returns audio URLs, which are rendered on the screen.

7. **Data Storage**  
   - All URLs of images and audio, along with the script, are saved in local storage.

8. **Final Video Generation**  
   - On the final screen, the saved URLs and script are sent to the backend.  
   - The backend generates the final video and returns its URL.  
   - The video is displayed on the final screen.
