/* oxlint-disable react/only-export-components -- route-level lazy components intentionally share the router module */
import { lazy } from 'react';
import { createBrowserRouter } from 'react-router-dom';

import { ProtectedRoute } from '../components/ProtectedRoute';
import { RoleRoute } from '../components/RoleRoute';
import { AuthLayout } from '../layouts/AuthLayout';
import { MainLayout } from '../layouts/MainLayout';
const CartPage = lazy(() => import('../pages/CartPage').then((module) => ({ default: module.CartPage })));
const CheckoutPage = lazy(() => import('../pages/CheckoutPage').then((module) => ({ default: module.CheckoutPage })));
const CanteenPage = lazy(() => import('../pages/CanteenPage').then((module) => ({ default: module.CanteenPage })));
const CanteenDashboardPage = lazy(() => import('../pages/CanteenDashboardPage').then((module) => ({ default: module.CanteenDashboardPage })));
const HomePage = lazy(() => import('../pages/HomePage').then((module) => ({ default: module.HomePage })));
const LoginPage = lazy(() => import('../pages/LoginPage').then((module) => ({ default: module.LoginPage })));
const ForgotPasswordPage = lazy(() => import('../pages/ForgotPasswordPage').then((module) => ({ default: module.ForgotPasswordPage })));
const ResetPasswordPage = lazy(() => import('../pages/ResetPasswordPage').then((module) => ({ default: module.ResetPasswordPage })));
const VerifyEmailPage = lazy(() => import('../pages/VerifyEmailPage').then((module) => ({ default: module.VerifyEmailPage })));
const LegalPage = lazy(() => import('../pages/LegalPage').then((module) => ({ default: module.LegalPage })));
const NotFoundPage = lazy(() => import('../pages/NotFoundPage').then((module) => ({ default: module.NotFoundPage })));
const OrderDetailPage = lazy(() => import('../pages/OrderDetailPage').then((module) => ({ default: module.OrderDetailPage })));
const PreferencesPage = lazy(() => import('../pages/PreferencesPage').then((module) => ({ default: module.PreferencesPage })));
const SupportPage = lazy(() => import('../pages/SupportPage').then((module) => ({ default: module.SupportPage })));
const MyOrdersPage = lazy(() => import('../pages/MyOrdersPage').then((module) => ({ default: module.MyOrdersPage })));
const OrderSuccessPage = lazy(() => import('../pages/OrderSuccessPage').then((module) => ({ default: module.OrderSuccessPage })));
const PaymentConfirmedPage = lazy(() => import('../pages/PaymentConfirmedPage').then((module) => ({ default: module.PaymentConfirmedPage })));
const PixPaymentPage = lazy(() => import('../pages/PixPaymentPage').then((module) => ({ default: module.PixPaymentPage })));
const ProfilePage = lazy(() => import('../pages/ProfilePage').then((module) => ({ default: module.ProfilePage })));
const RegisterPage = lazy(() => import('../pages/RegisterPage').then((module) => ({ default: module.RegisterPage })));
const RoleLandingPage = lazy(() => import('../pages/RoleLandingPage').then((module) => ({ default: module.RoleLandingPage })));
const SellerOrdersPage = lazy(() => import('../pages/SellerOrdersPage').then((module) => ({ default: module.SellerOrdersPage })));
const SellerSettingsPage = lazy(() => import('../pages/SellerSettingsPage').then((module) => ({ default: module.SellerSettingsPage })));
const WalletPage = lazy(() => import('../pages/WalletPage').then((module) => ({ default: module.WalletPage })));
const SellerOnboardingPage = lazy(() => import('../pages/SellerOnboardingPage').then((module) => ({ default: module.SellerOnboardingPage })));
const AdminCanteenModerationPage = lazy(() => import('../pages/AdminCanteenModerationPage').then((module) => ({ default: module.AdminCanteenModerationPage })));

export const router = createBrowserRouter([
  { path: '/termos', element: <LegalPage kind="terms" /> },
  { path: '/privacidade', element: <LegalPage kind="privacy" /> },
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
        path: '/esqueci-senha',
        element: <ForgotPasswordPage />,
      },
      {
        path: '/redefinir-senha',
        element: <ResetPasswordPage />,
      },
      {
        path: '/verificar-email',
        element: <VerifyEmailPage />,
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
            element: <RoleRoute allowedRoles={['customer']}><HomePage /></RoleRoute>,
          },
          {
            path: '/cantina/:id',
            element: <RoleRoute allowedRoles={['customer']}><CanteenPage /></RoleRoute>,
          },
          {
            path: '/carrinho',
            element: <RoleRoute allowedRoles={['customer']}><CartPage /></RoleRoute>,
          },
          {
            path: '/checkout',
            element: <RoleRoute allowedRoles={['customer']}><CheckoutPage /></RoleRoute>,
          },
          {
            path: '/pedidos/:orderId/sucesso',
            element: <RoleRoute allowedRoles={['customer']}><OrderSuccessPage /></RoleRoute>,
          },
          {
            path: '/pedidos/:orderId/pagamento-confirmado',
            element: <RoleRoute allowedRoles={['customer']}><PaymentConfirmedPage /></RoleRoute>,
          },
          {
            path: '/pagamentos/:transactionId/pix',
            element: <RoleRoute allowedRoles={['customer']}><PixPaymentPage /></RoleRoute>,
          },
          {
            path: '/pedidos',
            element: <RoleRoute allowedRoles={['customer']}><MyOrdersPage /></RoleRoute>,
          },
          {
            path: '/pedidos/:orderId',
            element: <RoleRoute allowedRoles={['customer']}><OrderDetailPage /></RoleRoute>,
          },
          {
            path: '/carteira',
            element: <RoleRoute allowedRoles={['customer']}><WalletPage /></RoleRoute>,
          },
          {
            path: '/perfil',
            element: <ProfilePage />,
          },
          {
            path: '/preferencias',
            element: <PreferencesPage />,
          },
          {
            path: '/suporte',
            element: <SupportPage />,
          },
          {
            path: '/entregas',
            element: <RoleRoute allowedRoles={['courier']}><RoleLandingPage title="Mural do entregador" description="Acompanhe e escolha as entregas disponíveis." /></RoleRoute>,
          },
          {
            path: '/vendedor/cardapio',
            element: <RoleRoute allowedRoles={['canteen_staff']}><CanteenDashboardPage /></RoleRoute>,
          },
          {
            path: '/vendedor/pedidos',
            element: <RoleRoute allowedRoles={['canteen_staff']}><SellerOrdersPage /></RoleRoute>,
          },
          {
            path: '/vendedor/horarios',
            element: <RoleRoute allowedRoles={['canteen_staff']}><SellerSettingsPage mode="hours" /></RoleRoute>,
          },
          {
            path: '/vendedor/configuracoes',
            element: <RoleRoute allowedRoles={['canteen_staff']}><SellerSettingsPage mode="settings" /></RoleRoute>,
          },
          {
            path: '/vendedor/onboarding',
            element: <RoleRoute allowedRoles={['canteen_staff']}><SellerOnboardingPage /></RoleRoute>,
          },
          {
            path: '/admin',
            element: <RoleRoute allowedRoles={['admin']}><AdminCanteenModerationPage /></RoleRoute>,
          },
        ],
      },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]);
