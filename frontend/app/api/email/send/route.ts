import { NextRequest, NextResponse } from "next/server";
import { sendWelcomeEmail } from "@/lib/resend";

export async function POST(request: NextRequest) {
  try {
    const { to, username } = await request.json();

    if (!to || !username) {
      return NextResponse.json(
        { error: "Missing required fields: to, username" },
        { status: 400 }
      );
    }

    const { data, error } = await sendWelcomeEmail(to, username);

    if (error) {
      console.error("[Resend] Failed to send welcome email:", error);
      return NextResponse.json({ error: "Failed to send email" }, { status: 500 });
    }

    return NextResponse.json({ success: true, id: data?.id });
  } catch (err) {
    console.error("[Resend] Unexpected error:", err);
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
