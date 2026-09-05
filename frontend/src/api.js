import axios from 'axios';

const api = axios.create({
  baseURL: 'https://moshiri.osdl.ir/api', 
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;