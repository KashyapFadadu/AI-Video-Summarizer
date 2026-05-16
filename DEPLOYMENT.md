# 🚀 Deployment Guide - AI Video Summarizer

Complete step-by-step guide to deploy your app on Streamlit Cloud for a live, shareable link.

---

## Phase 1: GitHub Setup (5 minutes)

### Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name**: `AI-Video-Summarizer`
   - **Description**: `An intelligent video summarization tool using AI models`
   - **Visibility**: Public (required for free Streamlit Cloud)
   - **Initialize with README**: NO (we have our own)
   - **Add .gitignore**: Python
   - **License**: MIT
3. Click **Create repository**

### Step 2: Push Your Code to GitHub

```bash
# Navigate to your project folder
cd f:\Projects\AI\ Video\ Summerizer

# Initialize git (if not already done)
git init

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/AI-Video-Summarizer.git

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: AI Video Summarizer with Streamlit"

# Push to GitHub
git branch -M main
git push -u origin main
```

**Verify**: Go to `https://github.com/YOUR_USERNAME/AI-Video-Summarizer` - you should see all your files!

---

## Phase 2: Streamlit Cloud Deployment (10 minutes)

### Step 1: Create Streamlit Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **Sign up** → Select **Continue with GitHub**
3. Authorize Streamlit to access your GitHub
4. Complete your profile

### Step 2: Deploy Your App

1. On Streamlit Cloud dashboard, click **New app**
2. Fill in deployment details:
   - **GitHub repo**: `YOUR_USERNAME/AI-Video-Summarizer`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. Click **Deploy!**

### Step 3: Wait for Deployment

- Initial deployment takes 2-3 minutes
- You'll see build logs in real-time
- Green checkmark ✅ = Success!
- Your app is now live! 🎉

**Your Live URL**: `https://ai-video-summarizer-YOUR_USERNAME.streamlit.app`

---

## Phase 3: Post-Deployment Steps

### Step 1: Test Your App

1. Click the URL to open your live app
2. Test all three input methods:
   - ✅ Upload a test video
   - ✅ Paste a transcript
   - ✅ Try a YouTube URL
3. Verify summaries are generated

### Step 2: Share Your App

**For Resume/Portfolio**:

```
📌 AI Video Summarizer
🔗 Live Demo: https://ai-video-summarizer-YOUR_USERNAME.streamlit.app
💻 GitHub: https://github.com/YOUR_USERNAME/AI-Video-Summarizer
```

**Social Media**:

> Check out my AI Video Summarizer! Built with Streamlit & HuggingFace models.
> Try it live: [URL] | Code: [GitHub URL] #AI #Python #Streamlit

### Step 3: Update README

In your `README.md`, find this line:

```markdown
👉 **[Try the live app here!](https://your-app-url.streamlit.app)**
```

Replace with your actual URL:

```markdown
👉 **[Try the live app here!](https://ai-video-summarizer-YOUR_USERNAME.streamlit.app)**
```

Push the change:

```bash
git add README.md
git commit -m "Update live app URL"
git push
```

---

## 📊 Monitoring & Maintenance

### Check App Status

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. View:
   - 📈 App usage stats
   - 🔴 Error logs
   - ⏱️ Response times
   - 💾 Memory usage

### Common Issues & Fixes

| Issue                            | Solution                                           |
| -------------------------------- | -------------------------------------------------- |
| **App crashes after 1GB memory** | Streamlit Cloud has 1GB limit; app is working fine |
| **First run slow**               | Models download on first use (2-3 min normal)      |
| **Video upload fails**           | Max file size is 200MB; Streamlit Cloud limit      |
| **"App crashed" error**          | Refresh page or restart from dashboard             |

### Restart Your App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **Settings** (⚙️) on your app
3. Click **Reboot** → **Confirm**

---

## 🔧 Updates & Maintenance

### Push Code Updates

Every time you update your code:

```bash
# In your local project
git add .
git commit -m "Description of changes"
git push origin main
```

**Streamlit Cloud automatically redeploys** within 1-2 minutes! 🚀

### Update Requirements

If you add new packages:

1. Update `requirements.txt`:

   ```bash
   pip freeze > requirements.txt
   ```

2. Push to GitHub:

   ```bash
   git add requirements.txt
   git commit -m "Update dependencies"
   git push
   ```

3. Streamlit Cloud will install new packages on next deploy!

---

## 📱 Share Your Live App

### LinkedIn Profile

```
AI Video Summarizer
🎬 Intelligent video summarization using state-of-the-art AI models
🔗 Live App: https://ai-video-summarizer-YOUR_USERNAME.streamlit.app
💻 GitHub: https://github.com/YOUR_USERNAME/AI-Video-Summarizer

Features:
✨ Upload, transcribe, and summarize videos
🤖 AI model comparison (PEGASUS, BART, T5)
🌍 Multi-language support with Whisper
⚙️ Customizable summaries

Stack: Python | Streamlit | HuggingFace | Whisper AI
```

### GitHub Badges

Add to your README for extra polish:

```markdown
![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)
![Live](https://img.shields.io/badge/Live-Streamlit%20Cloud-FF4B4B)
![Open Source](https://img.shields.io/badge/Open%20Source-MIT-green)
```

---

## ✅ Deployment Checklist

- [ ] GitHub account created
- [ ] Repository created and public
- [ ] Code pushed to main branch
- [ ] `.gitignore` includes temporary files
- [ ] `requirements.txt` updated with all dependencies
- [ ] `README.md` complete and professional
- [ ] `.streamlit/config.toml` created
- [ ] Streamlit account created
- [ ] App deployed on Streamlit Cloud
- [ ] Live URL tested and working
- [ ] App added to portfolio/resume
- [ ] GitHub link shared
- [ ] Live URL in README updated

---

## 🎓 Advanced Tips

### Custom Domain (Optional - Paid Feature)

1. Go to Streamlit Cloud dashboard
2. App Settings → Custom domain
3. Follow instructions to connect your domain

### Analytics

- Use Streamlit's built-in metrics in dashboard
- Track app performance and usage

### SEO for Your App

1. GitHub repo has descriptions
2. Share on Twitter/LinkedIn for visibility
3. Stack Overflow answers with your app link

---

## 🆘 Troubleshooting

### "Deploy failed" error

**Solution**:

```bash
# Verify requirements.txt has all imports
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Fix requirements"
git push
```

### App works locally but fails on Streamlit Cloud

**Check**:

- 1GB memory limit (model size issue?)
- All imports in `requirements.txt`
- No local file paths (use relative paths)

### Can't see GitHub repo during deploy

**Solution**:

1. Disconnect and reconnect GitHub in Streamlit settings
2. Make sure repo is PUBLIC
3. Refresh page and try again

---

## 📞 Support

- **Streamlit Help**: [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub Issues**: Create issue on your repo
- **Community**: [Streamlit Forum](https://discuss.streamlit.io)

---

## 🎉 You're Live!

Congratulations! Your app is now deployed and shareable.

**Next Steps**:

1. ✅ Test the live app thoroughly
2. ✅ Add to your portfolio
3. ✅ Share on social media
4. ✅ Include in job applications
5. ✅ Keep updating with new features

**Share this with confidence** 🚀

---

Last Updated: May 2026
