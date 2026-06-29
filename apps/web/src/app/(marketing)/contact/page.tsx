'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as zod from 'zod';
import { Section, SectionHeading } from '@/components/marketing/Section';
import { Field } from '@/components/forms/Field';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Mail, Phone, MapPin, CheckCircle } from 'lucide-react';
import { organizationSchema } from '@/lib/seo';

const contactSchema = zod.object({
  name: zod.string().min(2, 'Name must be at least 2 characters.'),
  email: zod.string().email('Please enter a valid email address.'),
  company: zod.string().optional(),
  subject: zod.string().min(4, 'Subject must be at least 4 characters.'),
  message: zod.string().min(10, 'Message must be at least 10 characters.'),
});

type ContactFormFields = zod.infer<typeof contactSchema>;

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ContactFormFields>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: '',
      email: '',
      company: '',
      subject: '',
      message: '',
    },
  });

  const onSubmit = async (data: ContactFormFields) => {
    // Simulate contact submission API
    await new Promise((resolve) => setTimeout(resolve, 800));
    console.log('[Contact Submission]', data);
    setSubmitted(true);
    reset();
  };

  const jsonLd = organizationSchema();

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Section className="pt-32">
        <SectionHeading
          eyebrow="Contact Us"
          title="We'd love to hear from you"
          description="Have questions about features, pricing, API access, or custom licensing? Drop us a line."
        />

        <div className="grid grid-cols-1 gap-12 lg:grid-cols-3 mt-12">
          {/* Info cards */}
          <div className="space-y-6 lg:col-span-1">
            <div className="rounded-2xl border border-slate-200 p-6 flex gap-4">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                <Mail size={18} />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 text-sm">General Support</h3>
                <p className="mt-1 text-sm text-slate-500">hello@nomen.ai</p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 p-6 flex gap-4">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                <Phone size={18} />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 text-sm">Sales Inquiry</h3>
                <p className="mt-1 text-sm text-slate-500">sales@nomen.ai</p>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 p-6 flex gap-4">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                <MapPin size={18} />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 text-sm">Corporate Office</h3>
                <p className="mt-1 text-sm text-slate-500">
                  100 Pine Street, Suite 1250<br />San Francisco, CA 94111
                </p>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="lg:col-span-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
              {submitted ? (
                <div className="flex flex-col items-center justify-center text-center py-12">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 mb-4">
                    <CheckCircle size={24} />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900">Message Sent!</h3>
                  <p className="mt-2 text-slate-500 max-w-sm">
                    Thank you for reaching out. A member of our team will follow up with you shortly.
                  </p>
                  <Button
                    onClick={() => setSubmitted(false)}
                    className="mt-6"
                    variant="secondary"
                  >
                    Send another message
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <Field label="Full Name" error={errors.name?.message}>
                      <Input
                        placeholder="John Doe"
                        error={!!errors.name}
                        {...register('name')}
                      />
                    </Field>
                    <Field label="Email Address" error={errors.email?.message}>
                      <Input
                        type="email"
                        placeholder="john@example.com"
                        error={!!errors.email}
                        {...register('email')}
                      />
                    </Field>
                  </div>

                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <Field label="Company / Organization" error={errors.company?.message}>
                      <Input
                        placeholder="Acme Corp (Optional)"
                        error={!!errors.company}
                        {...register('company')}
                      />
                    </Field>
                    <Field label="Subject" error={errors.subject?.message}>
                      <Input
                        placeholder="How can we help?"
                        error={!!errors.subject}
                        {...register('subject')}
                      />
                    </Field>
                  </div>

                  <Field label="Message" error={errors.message?.message}>
                    <textarea
                      rows={5}
                      placeholder="Please details your request or question..."
                      className={`flex w-full rounded-lg border bg-transparent px-3 py-2 text-sm ring-offset-white placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:placeholder:text-slate-500 dark:text-white ${
                        errors.message
                          ? 'border-red-500 focus-visible:ring-red-500'
                          : 'border-slate-200 focus-visible:ring-indigo-600'
                      }`}
                      {...register('message')}
                    />
                  </Field>

                  <Button type="submit" className="w-full sm:w-auto" isLoading={isSubmitting}>
                    Send Message
                  </Button>
                </form>
              )}
            </div>
          </div>
        </div>
      </Section>
    </>
  );
}
