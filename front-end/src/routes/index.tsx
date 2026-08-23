import { createBrowserRouter, Navigate } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { AuthLayout } from '../layouts/AuthLayout';
import { MainLayout } from '../layouts/MainLayout';
import { CartPage } from '../pages/CartPage';
import { CanteenPage } from '../pages/CanteenPage';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';

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
        ],
      },
    ],
  },
]);