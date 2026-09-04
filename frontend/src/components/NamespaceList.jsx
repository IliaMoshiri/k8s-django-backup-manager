import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Table, Button, Modal, Form, Input, Card, Popconfirm, message } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import api from '../api';

export default function NamespaceList() {
  const { clusterId } = useParams();
  const navigate = useNavigate();
  const [namespaces, setNamespaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  const fetchNamespaces = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/namespace?cluster_id=${clusterId}`);
      setNamespaces(res.data);
    } catch (err) {
      message.error('Failed to fetch namespaces');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNamespaces();
  }, [clusterId]);

  const handleCreate = async (values) => {
    try {
      await api.post('/namespace', { ...values, cluster_id: parseInt(clusterId) });
      message.success('Namespace created successfully');
      setIsModalOpen(false);
      form.resetFields();
      fetchNamespaces();
    } catch (err) {
      message.error('Failed to create namespace');
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/namespace/${id}`);
      message.success('Namespace deleted successfully');
      fetchNamespaces();
    } catch (err) {
      message.error('Failed to delete namespace');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Namespace Name', dataIndex: 'name', key: 'name' },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <>
          <Button type="link" onClick={() => navigate(`/namespaces/${record.id}/apps`)}>
            View Apps
          </Button>
          <Popconfirm title="Are you sure you want to delete this namespace?" onConfirm={() => handleDelete(record.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </>
      ),
    },
  ];

  return (
    <Card title={`Namespaces (Cluster ID: ${clusterId})`} extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>Create Namespace</Button>}>
      <Table dataSource={namespaces} columns={columns} rowKey="id" loading={loading} />
      <Modal title="Create New Namespace" open={isModalOpen} onCancel={() => setIsModalOpen(false)} onOk={() => form.submit()}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="name" label="Namespace Name" rules={[{ required: true }]}>
            <Input placeholder="e.g. staging" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}