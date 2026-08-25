import { Link, useParams } from 'react-router-dom';

export function OrderSuccessPage(): React.JSX.Element {
  const { orderId } = useParams();

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#fff1d6] px-5 text-center text-ilarica-ink">
      <section className="w-full max-w-lg rounded-3xl bg-white p-8 shadow-[0_18px_50px_rgba(122,30,30,0.08)] sm:p-10">
        <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[#eaf7ed] text-3xl text-[#287a38]" aria-hidden="true">✓</span>
        <h1 className="mt-5 font-display text-2xl font-extrabold text-[#7a1e1e]">Pedido confirmado!</h1>
        <p className="mt-3 text-sm leading-relaxed text-ilarica-muted">A cantina recebeu seu pedido. Você poderá acompanhar as próximas atualizações na área de pedidos.</p>
        {orderId && <p className="mt-4 break-all rounded-xl bg-[#fff1d6] px-4 py-3 text-xs text-ilarica-muted">Pedido: <strong className="text-ilarica-ink">{orderId}</strong></p>}
        <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
          <Link to="/pedidos" className="rounded-full bg-ilarica-orange px-6 py-3 text-sm font-bold text-white">Acompanhar pedido</Link>
          <Link to="/" className="rounded-full border border-ilarica-line px-6 py-3 text-sm font-bold text-[#7a1e1e]">Voltar ao Mural</Link>
        </div>
      </section>
    </main>
  );
}
