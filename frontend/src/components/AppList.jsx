import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Table, Button, Modal, Form, Input, InputNumber, Card, Badge, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import api from '../api';

export default function AppList() {
  const { namespaceId } = useParams();
  const navigate = useNavigate();
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchApps = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/app/?namespace_id=${namespaceId}`);
      setApps(res.data);
    } catch (err) {
      message.error('Failed to fetch apps list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApps();
  }, [namespaceId]);

  const handleCreate = async (values) => {
    try {
      await api.post('/app/', { ...values, namespace_id: parseInt(namespaceId) });
      message.success('App created successfully');
      setIsModalOpen(false);
      form.resetFields();
      fetchApps();
    } catch (err) {
      message.error('Failed to create app');
    }
  };

  const columns = [
    { title: 'App Name', dataIndex: 'name', key: 'name' },
    { title: 'Image', dataIndex: 'image', key: 'image' },
    { title: 'Replicas', dataIndex: 'replicas', key: 'replicas' },
    {
      title: 'Pods Status',
      key: 'pods',
      render: (_, record) => {
        if (typeof record.live_pods === 'string') {
          return <Badge status="warning" text={record.live_pods} />;
        }
        return (
          <span>
            {record.live_pods?.map((p, idx) => (
              <Badge
                key={idx}
                status={p.ready ? 'success' : 'processing'}
                text={`${p.pod_name} (${p.phase})`}
                style={{ display: 'block' }}
              />
            ))}
          </span>
        );
      },
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button type="primary" ghost onClick={() => navigate(`/apps/${record.id}`)}>
          Details & Edit
        </Button>
      ),
    },
  ];

  return (
    <Card title="Applications (Apps)" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>Create App</Button>}>
      <Table dataSource={apps} columns={columns} rowKey="id" loading={loading} />
      <Modal title="Create New Application" open={isModalOpen} onCancel={() => setIsModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleCreate} initialValues={{ replicas: 1, cpu: '100m', memory: '128Mi' }}>
          <Form.Item name="name" label="App Name" rules={[{ required: true }]}>
            <Input placeholder="e.g. web-api" />
          </Form.Item>
          <Form.Item name="image" label="Docker Image" rules={[{ required: true }]}>
            <Input placeholder="nginx:latest" />
          </Form.Item>
          <Form.Item name="replicas" label="Replicas Count">
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="cpu" label="CPU Limit">
            <Input />
          </Form.Item>
          <Form.Item name="memory" label="Memory Limit">
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}