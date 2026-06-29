# Component Guidelines: Nomen

This guide explains how to construct reusable, accessible, and high-performance UI components using the Nomen design system.

---

## 1. Composition Rules

- **`Button`**: Supports variants (`primary`, `secondary`, `outline`, `destructive`, `ghost`) and sizes. Micro-animations are managed automatically using Framer Motion.
- **`Card`**: Structured into component blocks to build complex layouts:
  - `CardHeader`: Labels wrapper.
  - `CardTitle`: Bold section headers.
  - `CardContent`: Center panel layout.
  - `CardFooter`: Actions tray.

---

## 2. Form System Validations

Form controls combine **React Hook Form** and **Zod** schema validations:

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Field } from '@/components/forms/Field';
import { Input } from '@/components/ui/Input';

const form = useForm({
  resolver: zodResolver(schema),
});

<Field label="Email" error={form.formState.errors.email?.message}>
  <Input {...form.register('email')} error={!!form.formState.errors.email} />
</Field>
```
This ensures consistent label spacing and validation warnings without duplicate markup.
