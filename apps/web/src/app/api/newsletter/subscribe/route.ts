import { NextResponse } from 'next/server';
import { subscribeToNewsletter } from '@/lib/newsletter';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email } = body;

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { success: false, message: 'Email address is required.' },
        { status: 400 }
      );
    }

    // Email regex validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { success: false, message: 'Please enter a valid email address.' },
        { status: 400 }
      );
    }

    const result = await subscribeToNewsletter(email);
    if (!result.success) {
      return NextResponse.json(
        { success: false, message: result.message },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true, message: result.message });
  } catch {
    return NextResponse.json(
      { success: false, message: 'Internal server error during subscription.' },
      { status: 500 }
    );
  }
}
