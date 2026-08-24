interface RoleLandingPageProps {
  title: string;
  description: string;
}

export function RoleLandingPage({ title, description }: RoleLandingPageProps): React.JSX.Element {
  return (
    <section className="rounded-2xl border border-orange-100 bg-white p-8 shadow-sm">
      <p className="text-sm font-semibold uppercase tracking-widest text-orange-600">iLarica</p>
      <h1 className="mt-2 text-3xl font-bold text-slate-900">{title}</h1>
      <p className="mt-3 text-slate-600">{description}</p>
    </section>
  );
}
