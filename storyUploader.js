require('dotenv').config({ path: '../.env' });
const fs = require('fs');
const path = require('path');
const pinataSDK = require('@pinata/sdk');
const { StoryClient, StoryConfig } = require('@story-protocol/core-sdk');
const { ethers } = require('ethers');
const { http, createPublicClient } = require('viem');

/**
 * Validate environment and configuration
 * @return {boolean} - Whether validation passed
 */
function validateEnvironment() {
  console.log('Validating environment...');
  
  // Check for required environment variables
  const requiredEnvVars = ['WALLET_PRIVATE_KEY', 'PINATA_JWT', 'RPC_PROVIDER_URL', 'PINATA_API', 'PINATA_API_SECRET'];
  const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

  if (missingEnvVars.length > 0) {
    console.error(`Missing required environment variables: ${missingEnvVars.join(', ')}`);
    console.error('Please add them to your .env file');
    return false;
  }
  
  try {
    // Test Pinata connection
    console.log('Testing Pinata connection...');
    const pinata = new pinataSDK(
      process.env.PINATA_API,
      process.env.PINATA_API_SECRET
    );
    
    // Test wallet creation
    console.log('Testing wallet creation...');
    const wallet = new ethers.Wallet(process.env.WALLET_PRIVATE_KEY);
    console.log(`Wallet address: ${wallet.address}`);
    
    // Test Story Protocol client creation
    console.log('Testing Story Protocol client creation...');
    const transport = http(process.env.RPC_PROVIDER_URL);
    
    const storyConfig = {
      wallet,
      transport,
      chainId: "aeneid",
    };
    
    try {
      const storyClient = new StoryClient(storyConfig);
      console.log('Story Protocol client created successfully');
    } catch (error) {
      console.error('Error creating Story Protocol client:', error.message);
      return false;
    }
    
    console.log('All environment checks passed!');
    return true;
  } catch (error) {
    console.error('Error during environment validation:', error.message);
    if (error.stack) {
      console.error('Stack trace:', error.stack);
    }
    return false;
  }
}

// Check for required environment variables
const requiredEnvVars = ['WALLET_PRIVATE_KEY', 'PINATA_JWT', 'RPC_PROVIDER_URL', 'PINATA_API', 'PINATA_API_SECRET'];
const missingEnvVars = requiredEnvVars.filter(envVar => !process.env[envVar]);

if (missingEnvVars.length > 0) {
  console.error(`Missing required environment variables: ${missingEnvVars.join(', ')}`);
  console.error('Please add them to your .env file');
  process.exit(1);
}

// Initialize Pinata client
const pinata = new pinataSDK(
  process.env.PINATA_API,
  process.env.PINATA_API_SECRET
);

console.log('Creating wallet...');
// Create wallet from private key
const wallet = new ethers.Wallet(process.env.WALLET_PRIVATE_KEY);
console.log(`Wallet address: ${wallet.address}`);

console.log('Setting up Story Protocol client...');
// Create the HTTP transport for viem
const transport = http(process.env.RPC_PROVIDER_URL);

// Setup Story Protocol client
const storyConfig = {
  wallet,
  transport,
  chainId: "aeneid",
};

const storyClient = new StoryClient(storyConfig);

/**
 * Upload an image to IPFS via Pinata
 * @param {string} imagePath - Path to the image file
 * @param {string} prompt - The prompt used to generate the image
 * @return {Promise<string>} - IPFS CID of the uploaded content
 */
async function uploadToIPFS(imagePath, prompt) {
  console.log(`Uploading ${imagePath} to IPFS via Pinata...`);
  
  try {
    // Check if file exists
    if (!fs.existsSync(imagePath)) {
      throw new Error(`File not found: ${imagePath}`);
    }
    
    // Read the image file
    const readableStreamForFile = fs.createReadStream(imagePath);
    
    // Prepare metadata
    const metadata = {
      name: `AI Generated Image: ${path.basename(imagePath)}`,
      description: `Image generated with the prompt: "${prompt}"`,
      keyvalues: {
        prompt: prompt,
        generationDate: new Date().toISOString(),
        source: 'AI Image Generator',
      }
    };

    console.log('Uploading file to Pinata...');
    // Upload to Pinata
    const result = await pinata.pinFileToIPFS(readableStreamForFile, {
      pinataMetadata: metadata
    });
    
    console.log(`Successfully uploaded to IPFS with CID: ${result.IpfsHash}`);
    return result.IpfsHash;
  } catch (error) {
    console.error('Error uploading to IPFS:', error.message);
    if (error.response) {
      console.error('Pinata API response:', error.response.data);
    }
    throw error;
  }
}

/**
 * Register an asset on Story Protocol
 * @param {string} ipfsCid - IPFS CID of the image
 * @param {string} prompt - The prompt used to generate the image
 * @return {Promise<Object>} - Result of the registration
 */
async function registerOnStoryProtocol(ipfsCid, prompt) {
  console.log('Registering on Story Protocol...');
  
  try {
    // Format creation date
    const creationDate = new Date().toISOString().split('T')[0];
    
    // Generate a title based on the prompt
    const title = `AI Generated: ${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}`;
    
    // Create metadata for the IP asset
    const metadata = {
      name: title,
      description: `AI-generated image using prompt: "${prompt}"`,
      mediaUrl: `ipfs://${ipfsCid}`,
      creationDate,
      contentType: 'IMAGE',
      tags: ['ai-generated', 'image']
    };
    
    console.log('Submitting transaction to Story Protocol...');
    
    // Register the IP asset on Story Protocol
    const registerParams = {
      tokenContractAddress: "", // Empty string for non-tokenized asset
      metadataURL: `ipfs://${ipfsCid}`,
      externalURL: `https://ipfs.io/ipfs/${ipfsCid}`,
      royaltyContext: {
        royaltyPercentage: 500, // 5% royalty
        rightholders: [{
          address: wallet.address,
          basisPoint: 10000 // 100% of royalties to the uploader
        }]
      }
    };
    
    console.log('Registration parameters:', JSON.stringify(registerParams, null, 2));
    
    const txHash = await storyClient.ipAsset.register(registerParams);
    
    console.log(`Transaction successful!`);
    console.log(`Transaction hash: ${txHash}`);
    console.log(`View transaction: https://explorer.aeneid.storyrpc.io/tx/${txHash}`);
    console.log(`View image: https://ipfs.io/ipfs/${ipfsCid}`);
    
    return {
      txHash,
      ipfsCid,
      title,
      viewUrl: `https://ipfs.io/ipfs/${ipfsCid}`,
      explorerUrl: `https://explorer.aeneid.storyrpc.io/tx/${txHash}`,
    };
  } catch (error) {
    console.error('Error registering on Story Protocol:', error.message);
    console.error('Stack trace:', error.stack);
    throw error;
  }
}

/**
 * Main function to upload an image and register it on Story Protocol
 * @param {string} imagePath - Path to the image file
 * @param {string} prompt - The prompt used to generate the image
 */
async function uploadToStoryProtocol(imagePath, prompt) {
  console.log('Starting upload to Story Protocol process...');
  console.log(`Image: ${imagePath}`);
  console.log(`Prompt: ${prompt}`);
  
  try {
    // Upload to IPFS
    const ipfsCid = await uploadToIPFS(imagePath, prompt);
    
    // Register on Story Protocol
    const result = await registerOnStoryProtocol(ipfsCid, prompt);
    
    // Write result to a file for Python to read
    fs.writeFileSync(
      path.join(__dirname, 'upload_result.json'),
      JSON.stringify(result, null, 2)
    );
    
    console.log('Complete! Result saved to upload_result.json');
    console.log('--------------- TRANSACTION SUMMARY ---------------');
    console.log(`Transaction hash: ${result.txHash}`);
    console.log(`Explorer URL: ${result.explorerUrl}`);
    console.log(`IPFS CID: ${result.ipfsCid}`);
    console.log(`View image: ${result.viewUrl}`);
    console.log('--------------------------------------------------');
    
    return result;
  } catch (error) {
    console.error('Error in uploadToStoryProtocol:', error.message);
    
    // Write error to a file for Python to read
    fs.writeFileSync(
      path.join(__dirname, 'upload_result.json'),
      JSON.stringify({ 
        error: error.message,
        timestamp: new Date().toISOString()
      }, null, 2)
    );
    
    throw error;
  }
}

// Handle command line arguments
if (require.main === module) {
  const args = process.argv.slice(2);
  
  // Check for test flag
  if (args.includes('--test')) {
    console.log('Running in test mode to validate environment...');
    const isValid = validateEnvironment();
    if (isValid) {
      console.log('✅ Environment validation successful! The Story Protocol integration is properly configured.');
      process.exit(0);
    } else {
      console.error('❌ Environment validation failed! Please check the error messages above.');
      process.exit(1);
    }
    return; // Don't continue to normal execution
  }
  
  // Regular execution mode
  if (args.length < 2) {
    console.error('Usage: node storyUploader.js <imagePath> <prompt>');
    console.error('   OR: node storyUploader.js --test (to validate environment)');
    process.exit(1);
  }
  
  const imagePath = args[0];
  const prompt = args[1];
  
  uploadToStoryProtocol(imagePath, prompt)
    .then(() => process.exit(0))
    .catch((error) => {
      console.error('Failed to upload:', error.message);
      process.exit(1);
    });
}

// Export functions for use in other modules
module.exports = {
  uploadToIPFS,
  registerOnStoryProtocol,
  uploadToStoryProtocol,
  validateEnvironment
}; 