import { _mock } from "./_mock";

export const _documents = Array.from({ length: 20 }, (_, index) => ({
  id: _mock.id(index),
  type: _mock.documentType(index),
  name: _mock.documentName(index),
  data_limit: _mock.chunkSize(index),
  time_limit: _mock.lastSynced(index),
  rate_limit: _mock.vectorDimensions(index),
  session_timeout: _mock.sessionTimeout(index),
  idle_timeout: _mock.idleTimeout(index),
  price: _mock.securityLevelNumber(index),
  status: _mock.documentStatus(index),
  validity_period: _mock.validityPeriod(index),
  features: _mock.features(index),
  subscribers: _mock.number.subscribers(index),
  description: _mock.sentence(index),
  created_at: _mock.time(index),
  updated_at: _mock.time(index),
}));
