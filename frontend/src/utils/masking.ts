export function maskIdentifier(val: string): string {
  if (!val) return '';
  const clean = val.trim();
  
  // 12-digit Aadhaar
  if (/^\d{4}\s\d{4}\s\d{4}$/.test(clean)) {
    return `XXXX XXXX ${clean.slice(-4)}`;
  }
  if (/^\d{12}$/.test(clean)) {
    return `XXXX XXXX ${clean.slice(-4)}`;
  }
  
  // 10-char PAN (5 letters, 4 digits, 1 letter)
  if (/^[A-Z]{5}\d{4}[A-Z]$/i.test(clean)) {
    return `XXXXX${clean.slice(5, 9)}${clean.slice(-1)}`;
  }
  
  // Driving licence / Passport
  if (clean.length > 8) {
    return `${clean.slice(0, 2)}****${clean.slice(-4)}`;
  }
  
  return clean;
}
