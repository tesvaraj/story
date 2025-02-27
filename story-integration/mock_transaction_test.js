require('dotenv').config({ path: '../.env' });
const fs = require('fs');
const path = require('path');

/**
 * Generate a mock transaction hash (66 characters including 0x prefix)
 */
function generateMockTxHash() {
  return '0x' + Array(64).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('');
}

/**
 * Generate a mock IPFS CID (46 characters starting with Qm)
 */
function generateMockIpfsCid() {
  return 'Qm' + Array(44).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('');
}

// Generate mock data
const mockTxHash = generateMockTxHash();
const mockIpfsCid = generateMockIpfsCid();

console.log('Generated mock transaction hash:');
console.log(mockTxHash);
console.log(`Length: ${mockTxHash.length}`);
console.log('\nGenerated mock IPFS CID:');
console.log(mockIpfsCid);
console.log(`Length: ${mockIpfsCid.length}`);

// Write to a file for testing
const resultObject = {
  txHash: mockTxHash,
  ipfsCid: mockIpfsCid,
  explorerUrl: `https://explorer.aeneid.storyrpc.io/tx/${mockTxHash}`,
  viewUrl: `https://ipfs.io/ipfs/${mockIpfsCid}`,
  title: 'Mock Transaction Test',
};

fs.writeFileSync(
  path.join(__dirname, 'upload_result.json'),
  JSON.stringify(resultObject, null, 2)
);

// Also create a human-readable debug file
fs.writeFileSync(
  path.join(__dirname, 'upload_result_debug.txt'),
  `Transaction Hash (string): ${resultObject.txHash}
Transaction Hash Length: ${resultObject.txHash.length}
IPFS CID: ${resultObject.ipfsCid}
IPFS CID Length: ${resultObject.ipfsCid.length}
Explorer URL: ${resultObject.explorerUrl}
View Image URL: ${resultObject.viewUrl}
Timestamp: ${new Date().toISOString()}`
);

console.log('\nMock data written to:');
console.log('- upload_result.json');
console.log('- upload_result_debug.txt'); 