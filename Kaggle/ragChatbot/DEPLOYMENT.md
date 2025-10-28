# 🚀 Streamlit Deployment Guide

Complete guide to run and deploy your RAG Chatbot web UI

---

## 📋 Table of Contents
1. [Local Development](#local-development)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Other Deployment Options](#other-deployment-options)
4. [Troubleshooting](#troubleshooting)

---

## 🏠 Local Development

### Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd ragChatbot

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install/update dependencies (including Streamlit)
pip install -r requirements.txt
```

### Step 2: Configure Secrets

Streamlit can read from either `.env` or `.streamlit/secrets.toml`:

**Option A: Use existing .env file (Recommended for local)**
```bash
# Your existing .env file already works!
# No additional setup needed
```

**Option B: Create Streamlit secrets file**
```bash
# Copy the template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit and add your API keys
nano .streamlit/secrets.toml  # or use your favorite editor
```

### Step 3: Run the App

```bash
# Start Streamlit
streamlit run app.py

# The app will open in your browser at:
# http://localhost:8501
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

### Step 4: Test the Interface

1. ✅ Chat interface loads
2. ✅ Sidebar settings appear
3. ✅ Database stats show up
4. ✅ Ask a test question
5. ✅ Response appears with sources

---

## ☁️ Streamlit Cloud Deployment

Deploy your app to the internet **for FREE** with Streamlit Cloud!

### Prerequisites

- GitHub account
- Your ragChatbot repository pushed to GitHub
- API keys ready (OpenAI, Anthropic, Pinecone)

### Step-by-Step Deployment

#### 1. Sign Up for Streamlit Cloud

```
1. Go to https://streamlit.io/cloud
2. Click "Sign up"
3. Sign in with GitHub
4. Authorize Streamlit to access your repositories
```

#### 2. Deploy Your App

```
1. Click "New app" in Streamlit Cloud dashboard
2. Select:
   - Repository: Simantini1709/ragChatbot
   - Branch: master
   - Main file path: app.py
3. Click "Advanced settings"
```

#### 3. Configure Secrets

In the "Secrets" section, paste your API keys:

```toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
PINECONE_API_KEY = "..."
PINECONE_ENVIRONMENT = "us-east-1-aws"
PINECONE_INDEX_NAME = "rag-chatbot-index"

# Optional: Override default settings
CHUNK_SIZE = "1000"
CHUNK_OVERLAP = "200"
TOP_K = "5"
TEMPERATURE = "0.7"
```

**IMPORTANT:**
- ⚠️ Never commit secrets.toml to GitHub
- ✅ Use Streamlit Cloud's secrets manager instead
- ✅ secrets.toml is already in .gitignore

#### 4. Deploy!

```
1. Click "Deploy"
2. Wait 2-3 minutes for build
3. Your app will be live at:
   https://[your-app-name].streamlit.app
```

### 5. Share Your App

Your public URL will look like:
```
https://ragchatbot-simantini.streamlit.app
```

**Perfect for:**
- 📱 LinkedIn portfolio
- 💼 Resume/CV projects section
- 🎤 Interview demos
- 👥 Sharing with recruiters

---

## 🎨 Customization

### Update App Appearance

Edit `app.py` to customize:

```python
# Change page title
st.set_page_config(
    page_title="My Custom Chatbot",
    page_icon="🎯",
)

# Modify colors in custom CSS
st.markdown("""
    <style>
    .user-message {
        background-color: #your-color;
    }
    </style>
""", unsafe_allow_html=True)
```

### Add Custom Branding

```python
# Add your logo
st.image("your-logo.png", width=200)

# Update footer
st.markdown("""
    Built by [Your Name](https://your-portfolio.com)
""")
```

---

## 🔧 Advanced Configuration

### Performance Optimization

**For faster loading:**

```python
# In app.py, add caching
@st.cache_resource
def initialize_chatbot():
    # Already implemented! ✅
    pass
```

**For better memory management:**

```bash
# Create .streamlit/config.toml (already created)
[server]
maxUploadSize = 50
enableXsrfProtection = true
```

### Custom Domain (Optional)

If you want a custom domain like `chat.yourcompany.com`:

1. Upgrade to Streamlit Team plan ($250/month)
2. Or use a reverse proxy (Nginx/Cloudflare)

**Free alternative:** Use a URL shortener
```
bit.ly/your-rag-chatbot
```

---

## 🐳 Other Deployment Options

### Option 1: Docker

```dockerfile
# Dockerfile (create this file)
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and run:**
```bash
docker build -t rag-chatbot .
docker run -p 8501:8501 --env-file .env rag-chatbot
```

### Option 2: Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku master
```

### Option 3: AWS EC2

```bash
# On EC2 instance
sudo apt update
sudo apt install python3-pip
pip install -r requirements.txt

# Run with nohup
nohup streamlit run app.py --server.port=8501 &
```

### Option 4: Google Cloud Run

```bash
# Use Docker image from above
gcloud run deploy rag-chatbot \
  --source . \
  --platform managed \
  --region us-central1
```

---

## 🐛 Troubleshooting

### Issue: App won't start locally

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue: "No API key found"

**Error:** `ValueError: OPENAI_API_KEY not found`

**Solution:**
1. Check `.env` file exists
2. Verify API keys are set
3. Restart Streamlit

```bash
# Verify .env file
cat .env | grep API_KEY

# Should show:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# PINECONE_API_KEY=...
```

---

### Issue: Streamlit Cloud deployment fails

**Error:** `Build failed`

**Check:**
1. All dependencies in `requirements.txt`
2. Secrets configured in Streamlit Cloud dashboard
3. Python version compatibility (use Python 3.9-3.11)

**Fix:** Add `runtime.txt`:
```bash
echo "python-3.9" > runtime.txt
git add runtime.txt
git commit -m "Add Python version"
git push
```

---

### Issue: Vector database connection error

**Error:** `Failed to connect to Pinecone`

**Solution:**
1. Check Pinecone API key is correct
2. Verify index exists
3. Check environment/region matches

```python
# Test Pinecone connection
python -c "from src.vector_store import VectorStore; vs = VectorStore(); print(vs.get_stats())"
```

---

### Issue: Slow performance

**Symptoms:** Long response times (>10 seconds)

**Solutions:**

1. **Reduce TOP_K:**
   ```python
   top_k = 3  # Instead of 5
   ```

2. **Use smaller embedding model:**
   ```bash
   # In .env
   EMBEDDING_MODEL=text-embedding-3-small  # Already using this ✅
   ```

3. **Cache responses:**
   ```python
   @st.cache_data
   def get_answer(question):
       return chatbot.ask(question)
   ```

---

### Issue: Out of memory on Streamlit Cloud

**Error:** `MemoryError`

**Solution:** Optimize imports and data loading
```python
# Instead of loading all at once
# Load components lazily
@st.cache_resource
def get_chatbot():
    return RAGChatbot()
```

---

## 📊 Monitoring & Analytics

### Track Usage

Add Google Analytics to `app.py`:

```python
# Add to main()
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'GA_MEASUREMENT_ID');
    </script>
""", unsafe_allow_html=True)
```

### Monitor Costs

Track API usage:
```python
# Add logging
import logging
logging.info(f"Query: {question}, TOP_K: {top_k}")
```

---

## 🔒 Security Best Practices

### ✅ Do's
- ✅ Use Streamlit secrets manager
- ✅ Keep .env in .gitignore
- ✅ Rotate API keys monthly
- ✅ Monitor usage for anomalies
- ✅ Use HTTPS (automatic on Streamlit Cloud)

### ❌ Don'ts
- ❌ Never commit API keys to GitHub
- ❌ Don't share secrets.toml file
- ❌ Don't use same keys for dev/prod
- ❌ Don't expose internal data paths

---

## 🎯 Next Steps

After successful deployment:

1. **Share on LinkedIn:**
   ```
   🚀 Just deployed my RAG chatbot!
   Try it live: [your-streamlit-url]
   ```

2. **Add to Resume:**
   ```
   Project: Enterprise RAG Chatbot
   Live Demo: [your-streamlit-url]
   GitHub: [your-github-url]
   ```

3. **Collect Feedback:**
   - Add feedback button in UI
   - Monitor analytics
   - Iterate based on usage

4. **Upgrade Features:**
   - Add user authentication
   - Implement rate limiting
   - Add chat export
   - Multi-language support

---

## 📞 Support

**Having issues?**

1. Check [Streamlit Docs](https://docs.streamlit.io)
2. Search [Streamlit Forum](https://discuss.streamlit.io)
3. Review [GitHub Issues](https://github.com/Simantini1709/ragChatbot/issues)
4. Contact me on [LinkedIn](https://linkedin.com/in/simantinighosh)

---

## 🎉 Success Checklist

Before sharing your app:

- [ ] App runs locally without errors
- [ ] All features working (chat, sources, filters)
- [ ] Deployed to Streamlit Cloud
- [ ] Public URL accessible
- [ ] Updated LinkedIn/portfolio
- [ ] Added to GitHub README
- [ ] Tested on mobile device
- [ ] Collected initial feedback

---

**🎊 Congratulations! Your RAG Chatbot is now live!**

Share it with the world and watch your portfolio shine! 🌟
