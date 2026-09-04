import React from 'react';
import { Empty, Button } from 'antd';

export default function CustomEmpty({ description, buttonText, onAction }) {
  return (
    <Empty
      image={Empty.PRESENTED_IMAGE_SIMPLE}
      description={description || 'No Data Available'}
    >
      {buttonText && onAction && (
        <Button type="primary" onClick={onAction}>
          {buttonText}
        </Button>
      )}
    </Empty>
  );
}