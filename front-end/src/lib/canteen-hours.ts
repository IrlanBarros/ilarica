export function formatNextOpening(value?: string | null): string | null {
  if (!value) return null;
  const opening = new Date(value);
  if (Number.isNaN(opening.getTime())) return null;

  const now = new Date();
  const time = new Intl.DateTimeFormat('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Fortaleza',
  }).format(opening);
  const openingDay = new Intl.DateTimeFormat('en-CA', {
    year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'America/Fortaleza',
  }).format(opening);
  const currentDay = new Intl.DateTimeFormat('en-CA', {
    year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'America/Fortaleza',
  }).format(now);
  const tomorrow = new Date(now.getTime() + 86_400_000);
  const tomorrowDay = new Intl.DateTimeFormat('en-CA', {
    year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'America/Fortaleza',
  }).format(tomorrow);

  if (openingDay === currentDay) return `Próxima abertura hoje às ${time}`;
  if (openingDay === tomorrowDay) return `Próxima abertura amanhã às ${time}`;
  const weekday = new Intl.DateTimeFormat('pt-BR', {
    weekday: 'long', timeZone: 'America/Fortaleza',
  }).format(opening);
  return `Próxima abertura ${weekday} às ${time}`;
}
