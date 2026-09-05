import React, { useEffect, useState } from 'react';
import { Table, Button, Modal, Form, Input, Card, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function ClusterList() {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const fetchClusters = async () => {
    setLoading(true);
    try {
      const res = await api.get('/cluster/');
      setClusters(res.data);
    } catch (err) {
      message.error('Failed to fetch clusters list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const handleCreate = async (values) => {
    try {
      await api.post('/cluster/', values);
      message.success('Cluster created successfully');
      setIsModalOpen(false);
      form.resetFields();
      fetchClusters();
    } catch (err) {
      message.error('Failed to create cluster');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Cluster Name', dataIndex: 'name', key: 'name' },
    { title: 'API Address', dataIndex: 'address', key: 'address' },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button type="primary" onClick={() => navigate(`/clusters/${record.id}/namespaces`)}>
          View Namespaces
        </Button>
      ),
    },
  ];

  return (
    <Card title="Cluster Management" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>Add Cluster</Button>}>
      <Table dataSource={clusters} columns={columns} rowKey="id" loading={loading} />
      <Modal title="Create New Cluster" open={isModalOpen} onCancel={() => setIsModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="name" label="Cluster Name" rules={[{ required: true }]}>
            <Input placeholder="e.g. k8s-production" />
          </Form.Item>
          <Form.Item name="address" label="API Address" rules={[{ required: true }]}>
            <Input placeholder="127.0.0.1:6443" />
          </Form.Item>
          <Form.Item name="token" label="Bearer Token" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}