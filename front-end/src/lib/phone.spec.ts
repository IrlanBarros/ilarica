import { describe, expect, it } from 'vitest';

import { formatBrazilianPhone, isValidBrazilianMobile, toBrazilianWhatsappPayload } from './phone';

describe('Brazilian WhatsApp formatting', () => {
  it('formats only the national number and adds +55 only to the API payload', () => {
    expect(formatBrazilianPhone('88981916231')).toBe('(88) 98191-6231');
    expect(toBrazilianWhatsappPayload('(88) 98191-6231')).toBe('5588981916231');
  });

  it('does not duplicate a pasted Brazilian country code', () => {
    expect(formatBrazilianPhone('+55 88 98191-6231')).toBe('(88) 98191-6231');
    expect(toBrazilianWhatsappPayload('+55 88 98191-6231')).toBe('5588981916231');
  });

  it('rejects incomplete and non-mobile national numbers', () => {
    expect(isValidBrazilianMobile('88 98191-6231')).toBe(true);
    expect(isValidBrazilianMobile('88 3819-1623')).toBe(false);
    expect(isValidBrazilianMobile('88 9819')).toBe(false);
  });
});
