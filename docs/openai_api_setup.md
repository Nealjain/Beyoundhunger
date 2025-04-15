# Setting Up the OpenAI API for Beyond Hunger Chatbot

This guide will walk you through getting and setting up an OpenAI API key for the Beyond Hunger chatbot.

## 1. Creating an OpenAI Account

1. Go to [OpenAI's website](https://openai.com)
2. Click on "Sign Up" to create a new account or "Log In" if you already have one
3. Complete the registration process with your email and password

## 2. Getting an API Key

1. After logging in, go to the [API Keys page](https://platform.openai.com/api-keys)
2. Click on "Create new secret key"
3. Give your key a name (e.g., "Beyond Hunger Chatbot")
4. Copy the key immediately - you won't be able to see it again!

## 3. Installing the OpenAI Package

Make sure the OpenAI Python package is installed in your environment:

```bash
# In your local environment
pip install openai

# On PythonAnywhere
pip3 install --user openai
```

## 4. Setting Up Your API Key in Beyond Hunger

1. Open `beyond_hunger/settings.py` in your project
2. Locate the OpenAI API key section (around line 300)
3. Replace the existing key with your new API key:
   ```python
   OPENAI_API_KEY = 'your-new-api-key-here'
   ```
4. Save the file

## 5. Deploying the Changes

### Local Testing:
1. Restart your Django server to apply the changes
2. Test the chatbot by sending a message

### PythonAnywhere Deployment:
1. Push your changes to GitHub (but first remove or hide the API key in a .env file)
2. Pull the changes on PythonAnywhere
3. Set up the API key as an environment variable in the `.env` file on PythonAnywhere
4. Reload your web app

## 6. Troubleshooting

If the chatbot isn't working properly, check the following:

1. **Console Errors**: Open your browser's console (F12) and check for errors when sending messages
2. **API Key Validity**: Ensure your API key is valid and has not expired
3. **Billing Setup**: Make sure your OpenAI account has billing set up (OpenAI requires a payment method)
4. **Rate Limits**: Check if you've hit rate limits on your OpenAI account
5. **Server Logs**: Check the Django server logs for any Python errors
6. **Package Version**: Ensure you're using a compatible version of the OpenAI package (try `pip install openai --upgrade`)

## 7. Best Practices for API Key Security

1. **Never commit your API key to Git**: Use environment variables or a .env file
2. **Restrict API key usage**: Set usage limits in your OpenAI dashboard
3. **Rotate keys periodically**: Create new keys and retire old ones every few months
4. **Monitor usage**: Regularly check your OpenAI dashboard for unusual activity

For more information, refer to [OpenAI's API Reference](https://platform.openai.com/docs/api-reference). 