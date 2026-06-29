export const animations = {
  transition: {
    default: { type: 'spring', stiffness: 300, damping: 30 },
    gentle: { type: 'spring', stiffness: 120, damping: 20 },
    slow: { duration: 0.4, ease: 'easeInOut' },
  },
  hover: {
    scale: 1.02,
    tap: 0.98,
  }
};
