# Leonardo

Generate video clip

Source: https://docs.leonardo.ai/docs/generate-motion-using-variation-images

	python3 -m venv env
	source env/bin/activate
	pip install requests
	python leonardo-video.py

motionStrength is set to max 10 since no movement occured at 5.

Remove the API key before commiting changes to GitHub.

We could integrate this script with our push to Github and run as a Google CoLab - where we could [store our API keys as Secrets](https://medium.com/@parthdasawant/how-to-use-secrets-in-google-colab-450c38e3ec75).