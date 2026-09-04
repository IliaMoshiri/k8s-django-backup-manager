import React, { useEffect, useState } from 'react';
import { Table, Tag, Card, Button, message } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import api from '../api';

export default function BackupList() {
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchBackups = async () => {
    setLoading(true);
    try {
      const res = await api.get('/backup/');
      setBackups(res.data);
    } catch (err) {
      message.error('Failed to fetch backup history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBackups();
  }, []);

  const columns = [
    { title: 'Backup ID', dataIndex: 'id', key: 'id' },
    { title: 'App Name', dataIndex: 'app_name', key: 'app_name' },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        let color = 'default';
        if (status === 'SUCCESS' || status === 'COMPLETED') color = 'green';
        if (status === 'PENDING' || status === 'RUNNING') color = 'blue';
        if (status === 'FAILED') color = 'red';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    { title: 'Created At', dataIndex: 'created_at', key: 'created_at' },
  ];

  return (
    <Card
      title="Backup Jobs History"
      extra={
        <Button icon={<ReloadOutlined />} onClick={fetchBackups}>
          Refresh
        </Button>
      }
    >
      <Table dataSource={backups} columns={columns} rowKey="id" loading={loading} />
    </Card>
  );
}