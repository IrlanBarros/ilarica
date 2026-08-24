import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { AuthLayout } from '../layouts/AuthLayout';
import { MainLayout } from '../layouts/MainLayout';
import { CartPage } from '../pages/CartPage';
import { CanteenPage } from '../pages/CanteenPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
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
            path: '/entregas',
            element: <RoleLandingPage title="Mural do entregador" description="Acompanhe e escolha as entregas disponíveis." />,
          },
          {
            path: '/vendedor/cardapio',
            element: <RoleLandingPage title="Gestão de cardápio" description="Gerencie os produtos e a disponibilidade da cantina." />,
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
