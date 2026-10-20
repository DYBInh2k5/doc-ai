# DocuMind AI 📄

AI-powered document intelligence platform built with Next.js 14, Supabase, and Pinecone embeddings.

## 🚀 Features

- **AI Document Search**: Semantic search across all your documents
- **Q&A Assistant**: Ask questions and get instant AI-powered answers
- **Smart Summaries**: Auto-generate document summaries
- **Team Collaboration**: Share documents with team members
- **Subscription Plans**: Free, Pro, and Enterprise tiers

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Authentication**: Clerk
- **Database**: Supabase (PostgreSQL)
- **Vector DB**: Pinecone (for AI embeddings)
- **AI**: OpenAI GPT-4
- **Payments**: Stripe
- **Email**: Resend
- **Caching**: Upstash Redis
- **Analytics**: PostHog
- **Error Tracking**: Sentry
- **Deployment**: Vercel
- **DNS**: Cloudflare


```
## 📖 Documentation

- ✅ **Analytics** - PostHog user tracking
- 🔜 API access for Enterprise
│   ├── app/              # Next.js App Router
│   │   ├── pricing/      # Pricing page
---
title: Doc AI
emoji: 📚
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
---

# Doc AI

 Ứng dụng hỏi đáp tài liệu PDF/TXT bằng FastAPI và giao diện web đơn giản.

 ## Tính năng

 - Đăng ký và đăng nhập bằng JWT.
 - Tải lên file PDF hoặc TXT.
 - Hỏi đáp theo nội dung tài liệu.
 - Trả lời kèm đoạn trích liên quan.
 - Lưu lịch sử hội thoại.
 - Hỗ trợ OpenAI hoặc Groq qua API tương thích OpenAI.

 ## Chạy local

 ```powershell
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1
 pip install -r requirements.txt
 Copy-Item .env.example .env
 uvicorn app.main:app --reload
 ```

 Mở `http://127.0.0.1:8000`.

 Để bật câu trả lời bằng AI, điền vào `.env`:

 ```env
 OPENAI_API_KEY=your-key
 OPENAI_MODEL=llama-3.3-70b-versatile
 OPENAI_BASE_URL=https://api.groq.com/openai/v1
 ```

 Không commit file `.env` hoặc API key lên GitHub.

 ## Deploy Render

Repository có sẵn `Dockerfile` và `render.yaml`. Trên Hugging Face Spaces chọn **Docker Space**, kết nối hoặc upload repository này, rồi thêm `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL` và `JWT_SECRET` trong Settings > Variables and secrets.

 SQLite và file upload trên gói free có thể mất khi service khởi động lại. Khi dùng thật, nên chuyển sang PostgreSQL và object storage.
│   │   └── page.tsx      # Landing page
│   ├── lib/              # Shared utilities
│   │   ├── supabase.ts   # Database client
│   │   ├── stripe.ts     # Payment client
│   │   ├── pinecone.ts   # Vector DB
│   │   ├── openai.ts     # AI functions
│   │   └── ...
│   └── types/            # TypeScript types
├── supabase_schema.sql   # Database schema
└── .env.local            # Environment variables
```

## 🔧 Tech Stack Details

| Category | Technology | Purpose |
|----------|-----------|---------|
| Frontend | Next.js 14 + TypeScript | React framework |
| Styling | Tailwind CSS | Utility-first CSS |
| Auth | Clerk | User management |
| Database | Supabase | PostgreSQL + RLS |
| Vector DB | Pinecone | AI embeddings |
| AI | OpenAI GPT-4 | Text generation |
| Payments | Stripe | Subscriptions |
| Email | Resend | Transactional emails |
| Cache | Upstash Redis | Rate limiting |
| Analytics | PostHog | User tracking |
| Monitoring | Sentry | Error tracking |
| Hosting | Vercel | Serverless deployment |
| DNS/CDN | Cloudflare | Security & performance |

## 💰 Pricing Plans

| Plan | Price | Documents | Queries | Target Users |
|------|-------|-----------|---------|--------------|
| Free | $0/mo | 10 | 100/mo | Individuals testing |
| Pro | $19/mo | 1,000 | Unlimited | Power users |
| Enterprise | $99/mo | Unlimited | Unlimited | Teams & businesses |

## 🚀 Deployment

### Deploy to Vercel (5 minutes)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Or use [Vercel Dashboard](https://vercel.com) to import from GitHub.

**See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete guide.**

## 🧪 Testing

### Test Locally

```bash
# Start dev server
npm run dev

# Test features:
# 1. Sign up at /sign-up
# 2. Upload document at /dashboard
# 3. Ask questions in search
# 4. Test payment at /pricing (use 4242 4242 4242 4242)
```

### Stripe Test Cards

- **Success**: 4242 4242 4242 4242
- **Declined**: 4000 0000 0000 0002

## 📊 Monitoring

- **Errors**: [sentry.io](https://sentry.io)
- **Analytics**: [posthog.com](https://posthog.com)
- **Payments**: [stripe.com/dashboard](https://stripe.com/dashboard)
- **Database**: [supabase.com/dashboard](https://supabase.com/dashboard)

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
