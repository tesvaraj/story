require('dotenv').config({ path: '../.env' });
const fs = require('fs');
const path = require('path');
const { StoryClient } = require('@story-protocol/core-sdk');
const { http } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const pinataSDK = require('@pinata/sdk');

/**
 * Test script to verify hash formats from Story Protocol and Pinata
 */
async function testHashes() {
  console.log('=== Testing Hash Formats ===');

  try {
    // Initialize Pinata client
    const pinata = new pinataSDK(
      process.env.PINATA_API,
      process.env.PINATA_API_SECRET
    );

    // Create account
    const privateKey = `0x${process.env.WALLET_PRIVATE_KEY.replace(/^0x/, '')}`;
    const account = privateKeyToAccount(privateKey);
    console.log(`Account address: ${account.address}`);

    // Setup Story Protocol client
    const config = {
      account: account,
      transport: http(process.env.RPC_PROVIDER_URL),
      chainId: "aeneid",
    };

    const storyClient = StoryClient.newClient(config);
    
    // Create a simple test file
    const testFilePath = path.join(__dirname, 'test_file.txt');
    fs.writeFileSync(testFilePath, 'This is a test file to verify hash formats');
    
    console.log('Uploading test file to Pinata...');
    // Upload to Pinata
    const readableStreamForFile = fs.createReadStream(testFilePath);
    const result = await pinata.pinFileToIPFS(readableStreamForFile, {
      pinataMetadata: { name: 'Test File' }
    });
    
    console.log(`IPFS Hash from Pinata: ${result.IpfsHash}`);
    console.log(`IPFS Hash length: ${result.IpfsHash.length}`);
    
    // Clean up
    fs.unlinkSync(testFilePath);
    
    // Log the results to a file
    fs.writeFileSync(
      path.join(__dirname, 'hash_test_result.json'),
      JSON.stringify({
        ipfsCid: result.IpfsHash,
        ipfsCidLength: result.IpfsHash.length,
        timestamp: new Date().toISOString()
      }, null, 2)
    );
    
    console.log('Test completed successfully');
    
  } catch (error) {
    console.error('Error in test:', error.message);
    if (error.stack) {
      console.error('Stack trace:', error.stack);
    }
  }
}

// Run the test
testHashes().then(() => {
  console.log('Test finished');
}); 