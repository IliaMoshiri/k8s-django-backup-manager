import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ConfigProvider, theme, Layout, Typography } from 'antd';
import ClusterList from './components/ClusterList';
import NamespaceList from './components/NamespaceList';
import AppList from './components/AppList';
import AppDetail from './components/AppDetail';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

export default function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#177ddc',
          colorBgContainer: '#1f1f1f',
        },
      }}
    >
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Header style={{ display: 'flex', alignItems: 'center' }}>
            <Link to="/" style={{ textDecoration: 'none' }}>
              <Title level={3} style={{ color: '#fff', margin: 0 }}>
                ⚙️ K8s Backup Manager
              </Title>
            </Link>
          </Header>
          <Content style={{ padding: '24px 50px' }}>
            <Routes>
              <Route path="/" element={<ClusterList />} />
              <Route path="/clusters/:clusterId/namespaces" element={<NamespaceList />} />
              <Route path="/namespaces/:namespaceId/apps" element={<AppList />} />
              <Route path="/apps/:appId" element={<AppDetail />} />
            </Routes>
          </Content>
          <Footer style={{ textAlign: 'center', background: '#141414' }}>
            K8s Backup Manager ©2026
          </Footer>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}