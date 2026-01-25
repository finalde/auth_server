import { ReactNode } from 'react';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="layout">
      <TopBar />
      <div className="layout-content">
        <Sidebar />
        <main className="main-panel">{children}</main>
      </div>
    </div>
  );
}
