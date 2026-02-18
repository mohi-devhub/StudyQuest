import { Resend } from "resend";

export const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendWelcomeEmail(to: string, username: string) {
  return resend.emails.send({
    from: "StudyQuest <onboarding@resend.dev>",
    to,
    subject: "Welcome to StudyQuest // ACCOUNT_CREATED",
    html: `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Welcome to StudyQuest</title>
  <style>
    body {
      background-color: #000000;
      color: #ffffff;
      font-family: 'Courier New', Courier, monospace;
      margin: 0;
      padding: 0;
    }
    .container {
      max-width: 560px;
      margin: 40px auto;
      padding: 40px;
      border: 1px solid #ffffff;
    }
    .label {
      color: #6b7280;
      font-size: 12px;
      margin-bottom: 24px;
    }
    h1 {
      font-size: 28px;
      font-weight: bold;
      margin: 0 0 8px 0;
    }
    .tagline {
      color: #9ca3af;
      font-size: 14px;
      margin-bottom: 32px;
    }
    .divider {
      border: none;
      border-top: 1px solid #374151;
      margin: 32px 0;
    }
    .feature-list {
      list-style: none;
      padding: 0;
      margin: 0 0 32px 0;
    }
    .feature-list li {
      color: #d1d5db;
      font-size: 14px;
      padding: 6px 0;
    }
    .cta-box {
      border: 1px solid #ffffff;
      padding: 16px 24px;
      text-align: center;
      margin-bottom: 32px;
    }
    .cta-box p {
      color: #9ca3af;
      font-size: 13px;
      margin: 0 0 12px 0;
    }
    .footer {
      color: #4b5563;
      font-size: 11px;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="label">// ACCOUNT_CREATED</div>
    <h1>StudyQuest</h1>
    <p class="tagline">Welcome, ${username}. Your learning profile is ready.</p>
    <hr class="divider" />
    <p style="color: #9ca3af; font-size: 14px; margin: 0 0 16px 0;">
      Please check your inbox for a separate verification email from Supabase
      and click the link to activate your account before logging in.
    </p>
    <hr class="divider" />
    <p style="color: #6b7280; font-size: 12px; margin: 0 0 12px 0;">// ACCOUNT_FEATURES</p>
    <ul class="feature-list">
      <li>→ Personalized AI study notes</li>
      <li>→ Adaptive quiz generation</li>
      <li>→ XP &amp; level progression system</li>
      <li>→ Achievement badges &amp; milestones</li>
      <li>→ Real-time progress tracking</li>
    </ul>
    <div class="cta-box">
      <p>Once verified, log in to start your learning journey.</p>
      <strong style="font-size: 14px;">studyquest.app // READY_TO_LEARN</strong>
    </div>
    <div class="footer">
      <p>StudyQuest v1.0 // Powered by Resend</p>
      <p style="margin-top: 4px;">You received this because you signed up at StudyQuest.</p>
    </div>
  </div>
</body>
</html>
    `,
  });
}
