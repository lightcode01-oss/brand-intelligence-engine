/**
 * Newsletter provider abstraction.
 *
 * Supports Mailchimp, ConvertKit, Resend, and a Mock implementation.
 * Provider is driven by NEWSLETTER_PROVIDER environment variable.
 */

export type NewsletterProvider = 'mailchimp' | 'convertkit' | 'resend' | 'mock';

export interface SubscribeResult {
  success: boolean;
  message: string;
}

/**
 * Subscribes an email address to the newsletter.
 * Called server-side only (API route or Server Action).
 */
export async function subscribeToNewsletter(
  email: string,
  tags?: string[]
): Promise<SubscribeResult> {
  const provider = (process.env.NEWSLETTER_PROVIDER || 'mock') as NewsletterProvider;

  switch (provider) {
    case 'mailchimp':
      return subscribeMailchimp(email, tags);
    case 'convertkit':
      return subscribeConvertKit(email);
    case 'resend':
      return subscribeResend(email);
    case 'mock':
    default:
      return subscribeMock(email);
  }
}

// ---------------------------------------------------------------------------
// Provider implementations
// ---------------------------------------------------------------------------

async function subscribeMailchimp(email: string, tags?: string[]): Promise<SubscribeResult> {
  const apiKey = process.env.MAILCHIMP_API_KEY;
  const listId = process.env.MAILCHIMP_LIST_ID;
  const dc = apiKey?.split('-')[1] || 'us1';

  if (!apiKey || !listId) {
    return { success: false, message: 'Mailchimp is not configured.' };
  }

  try {
    const res = await fetch(`https://${dc}.api.mailchimp.com/3.0/lists/${listId}/members`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email_address: email,
        status: 'subscribed',
        tags: tags || [],
      }),
    });

    if (res.ok) {
      return { success: true, message: "You're subscribed! Welcome to the Nomen community." };
    }
    const body = await res.json();
    if (body.title === 'Member Exists') {
      return { success: true, message: "You're already subscribed. Thank you!" };
    }
    return { success: false, message: 'Subscription failed. Please try again.' };
  } catch {
    return { success: false, message: 'Network error. Please try again.' };
  }
}

async function subscribeConvertKit(email: string): Promise<SubscribeResult> {
  const apiKey = process.env.CONVERTKIT_API_KEY;
  const formId = process.env.CONVERTKIT_FORM_ID;

  if (!apiKey || !formId) {
    return { success: false, message: 'ConvertKit is not configured.' };
  }

  try {
    const res = await fetch(`https://api.convertkit.com/v3/forms/${formId}/subscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey, email }),
    });

    if (res.ok) {
      return { success: true, message: "You're subscribed! Welcome to the Nomen community." };
    }
    return { success: false, message: 'Subscription failed. Please try again.' };
  } catch {
    return { success: false, message: 'Network error. Please try again.' };
  }
}

async function subscribeResend(email: string): Promise<SubscribeResult> {
  const apiKey = process.env.RESEND_API_KEY;
  const audienceId = process.env.RESEND_AUDIENCE_ID;

  if (!apiKey || !audienceId) {
    return { success: false, message: 'Resend is not configured.' };
  }

  try {
    const res = await fetch(`https://api.resend.com/audiences/${audienceId}/contacts`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (res.ok) {
      return { success: true, message: "You're subscribed! Welcome to the Nomen community." };
    }
    return { success: false, message: 'Subscription failed. Please try again.' };
  } catch {
    return { success: false, message: 'Network error. Please try again.' };
  }
}

async function subscribeMock(email: string): Promise<SubscribeResult> {
  // Simulate network latency in development
  await new Promise((resolve) => setTimeout(resolve, 500));
  console.log(`[Newsletter Mock] Subscribed: ${email}`);
  return { success: true, message: "You're subscribed! Welcome to the Nomen community." };
}
