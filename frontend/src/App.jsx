import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ConfigProvider, theme, Layout, Menu, Typography } from 'antd';
import { ClusterOutlined, HistoryOutlined } from '@ant-design/icons';
import ClusterList from './components/ClusterList';
import NamespaceList from './components/NamespaceList';
import AppList from './components/AppList';
import AppDetail from './components/AppDetail';
import BackupList from './components/BackupList';

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

export default function App() {
  const menuItems = [
    {
      key: 'clusters',
      icon: <ClusterOutlined />,
      label: <Link to="/">Clusters</Link>,
    },
    {
      key: 'backups',
      icon: <HistoryOutlined />,
      label: <Link to="/backups">Backup Logs</Link>,
    },
  ];

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
        <Layout style={{ height: '100vh', width: '100vw', overflow: 'hidden' }}>
          <Header style={{ display: 'flex', alignItems: 'center', height: '64px' }}>
            <Link to="/" style={{ textDecoration: 'none' }}>
              <Title level={3} style={{ color: '#fff', margin: 0 }}>
                ⚙️ K8s Backup Manager
              </Title>
            </Link>
          </Header>
          <Layout style={{ height: 'calc(100vh - 96px)' }}>
            <Sider width={200} style={{ background: '#1f1f1f' }}>
              <Menu
                mode="inline"
                defaultSelectedKeys={['clusters']}
                style={{ height: '100%', borderRight: 0 }}
                items={menuItems}
              />
            </Sider>
            <Content style={{ padding: '24px', overflowY: 'auto' }}>
              <Routes>
                <Route path="/" element={<ClusterList />} />
                <Route path="/clusters/:clusterId/namespaces" element={<NamespaceList />} />
                <Route path="/namespaces/:namespaceId/apps" element={<AppList />} />
                <Route path="/apps/:appId" element={<AppDetail />} />
                <Route path="/backups" element={<BackupList />} />
              </Routes>
            </Content>
          </Layout>
          <Footer style={{ textAlign: 'center', background: '#141414', height: '32px', padding: '6px 0' }}>
            K8s Backup Manager ©2026
          </Footer>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}