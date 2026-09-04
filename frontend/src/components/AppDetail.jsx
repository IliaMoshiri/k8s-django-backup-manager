import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Input, InputNumber, Button, Descriptions, Popconfirm, message, Space, Divider } from 'antd';
import { DeleteOutlined, SaveOutlined, CloudUploadOutlined } from '@ant-design/icons';
import api from '../api';

export default function AppDetail() {
  const { appId } = useParams();
  const navigate = useNavigate();
  const [appData, setAppData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/app?namespace_id=1`);
      const found = res.data.find((a) => a.id === parseInt(appId));
      if (found) {
        setAppData(found);
        form.setFieldsValue(found);
      }
    } catch (err) {
      message.error('Failed to fetch app details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [appId]);

  const handleUpdate = async (values) => {
    try {
      await api.put(`/app/${appId}`, values);
      message.success('App updated successfully');
      fetchDetail();
    } catch (err) {
      message.error('Failed to update app');
    }
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/app/${appId}`);
      message.success('App deleted successfully');
      navigate(-1);
    } catch (err) {
      message.error('Failed to delete app');
    }
  };

  const handleBackup = async () => {
    try {
      const res = await api.post('/backup/', {
        app_id: parseInt(appId),
        source_path: '/tmp/data',
      });
      message.success(`Backup task queued ID: ${res.data.backup_id}`);
    } catch (err) {
      message.error('Failed to trigger backup');
    }
  };

  if (!appData) return null;

  return (
    <Card title={`Application Details: ${appData.name}`} loading={loading}>
      <Descriptions bordered column={2}>
        <Descriptions.Item label="App ID">{appData.id}</Descriptions.Item>
        <Descriptions.Item label="Created At">{appData.created_at}</Descriptions.Item>
      </Descriptions>

      <Divider>Configuration & Updates</Divider>

      <Form form={form} layout="vertical" onFinish={handleUpdate}>
        <Form.Item name="image" label="Docker Image">
          <Input />
        </Form.Item>
        <Form.Item name="replicas" label="Replicas">
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="cpu" label="CPU Limit">
          <Input />
        </Form.Item>
        <Form.Item name="memory" label="Memory Limit">
          <Input />
        </Form.Item>
        <Space style={{ marginTop: 16 }}>
          <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
            Save Changes
          </Button>
          <Button icon={<CloudUploadOutlined />} onClick={handleBackup}>
            Trigger Backup
          </Button>
          <Popconfirm title="Are you sure you want to delete this app?" onConfirm={handleDelete}>
            <Button danger icon={<DeleteOutlined />}>
              Delete App
            </Button>
          </Popconfirm>
        </Space>
      </Form>
    </Card>
  );
}