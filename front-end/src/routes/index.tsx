import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { AuthLayout } from '../layouts/AuthLayout';
import { MainLayout } from '../layouts/MainLayout';
import { CartPage } from '../pages/CartPage';
import { CheckoutPage } from '../pages/CheckoutPage';
import { CanteenPage } from '../pages/CanteenPage';
import { CanteenDashboardPage } from '../pages/CanteenDashboardPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { OrderSuccessPage } from '../pages/OrderSuccessPage';
import { PaymentConfirmedPage } from '../pages/PaymentConfirmedPage';
import { PixPaymentPage } from '../pages/PixPaymentPage';
import { RegisterPage } from '../pages/RegisterPage';
import { RoleLandingPage } from '../pages/RoleLandingPage';

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      {
        path: '/login',
        element: <LoginPage />,
      },
      {
        path: '/cadastro',
        element: <RegisterPage />,
      },
      {
        path: '*',
        element: <Navigate to="/login" replace />,
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <MainLayout />,
        children: [
          {
            path: '/',
            element: <HomePage />,
          },
          {
            path: '/cantina/:id',
            element: <CanteenPage />,
          },
          {
            path: '/carrinho',
            element: <CartPage />,
          },
          {
            path: '/checkout',
            element: <CheckoutPage />,
          },
          {
            path: '/pedidos/:orderId/sucesso',
            element: <OrderSuccessPage />,
          },
          {
            path: '/pedidos/:orderId/pagamento-confirmado',
            element: <PaymentConfirmedPage />,
          },
          {
            path: '/pagamentos/:transactionId/pix',
            element: <PixPaymentPage />,
          },
          {
            path: '/pedidos',
            element: <RoleLandingPage title="Meus pedidos" description="Acompanhe seus pedidos em andamento e seu histórico." />,
          },
          {
            path: '/carteira',
            element: <RoleLandingPage title="Carteira" description="Consulte seu saldo e suas movimentações." />,
          },
          {
            path: '/perfil',
            element: <RoleLandingPage title="Meu perfil" description="Confira e atualize seus dados pessoais." />,
          },
          {
            path: '/entregas',
            element: <RoleLandingPage title="Mural do entregador" description="Acompanhe e escolha as entregas disponíveis." />,
          },
          {
            path: '/vendedor/cardapio',
            element: <CanteenDashboardPage />,
          },
          {
            path: '/admin',
            element: <RoleLandingPage title="Administração" description="Fundação da área administrativa do iLarica." />,
          },
        ],
      },
    ],
  },
]);
