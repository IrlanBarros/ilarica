const BRAZIL_COUNTRY_CODE = '55';
const NATIONAL_PHONE_LENGTH = 11;

export function brazilianPhoneDigits(value: string): string {
  const digits = value.replace(/\D/g, '');
  const nationalDigits = digits.startsWith(BRAZIL_COUNTRY_CODE) && digits.length > NATIONAL_PHONE_LENGTH
    ? digits.slice(BRAZIL_COUNTRY_CODE.length)
    : digits;
  return nationalDigits.slice(0, NATIONAL_PHONE_LENGTH);
}

export function formatBrazilianPhone(value: string): string {
  const digits = brazilianPhoneDigits(value);
  if (!digits) return '';
  if (digits.length <= 2) return `(${digits}`;
  if (digits.length <= 7) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
}

export function toBrazilianWhatsappPayload(value: string): string {
  return `${BRAZIL_COUNTRY_CODE}${brazilianPhoneDigits(value)}`;
}

export function isValidBrazilianMobile(value: string): boolean {
  const digits = brazilianPhoneDigits(value);
  return digits.length === NATIONAL_PHONE_LENGTH && digits[2] === '9';
}
