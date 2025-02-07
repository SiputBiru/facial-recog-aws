import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid/dist/esm/index.js';

const API_URL = 'yourAPIURL';
const BUCKET = 'rekog-visitor-pics';

function App() {
  const [image, setImage] = useState(null);
  const [uploadResultMessage, setUploadResultMessage] = useState('Please upload an image');
  const [isLoading, setIsLoading] = useState(false);
  const [isAuth, setAuth] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setUploadResultMessage('Please select an image file');
        return;
      }
      setImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const sendImage = async (e) => {
    e.preventDefault();
    if (!image) {
      setUploadResultMessage('Please select an image first');
      return;
    }

    setIsLoading(true);
    setUploadResultMessage('Processing...');

    try {
      const visitorImageName = uuidv4();
      const fileName = `${visitorImageName}.jpeg`;

      await fetch(`${API_URL}/${BUCKET}/${fileName}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'image/jpeg',
        },
        body: image,
      });

      const response = await authenticate(visitorImageName);
      
      if (response?.Message === 'Success') {
        setAuth(true);
        setUploadResultMessage(`Hi ${response.firstName} ${response.lastName}, welcome to work!`);
      } else {
        setAuth(false);
        setUploadResultMessage('Authentication failed');
      }
    } catch (err) {
      setAuth(false);
      setUploadResultMessage('Authentication process failed. Please try again.');
      console.error('Authentication error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const authenticate = async (visitorImageName) => {
    const params = new URLSearchParams({
      objectKey: `${visitorImageName}.jpeg`
    });
    
    try {
      const response = await fetch(`${API_URL}/employee?${params}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API error:', error);
      throw error;
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Company Face Recognition App</h1>
      <form onSubmit={sendImage} className="space-y-4">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="block w-full"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!image || isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {isLoading ? 'Processing...' : 'Authenticate'}
        </button>
      </form>
      
      <div className={`mt-4 p-2 rounded ${isAuth ? 'bg-green-100' : 'bg-red-100'}`}>
        {uploadResultMessage}
      </div>
      
      {previewUrl && (
        <div className="mt-4">
          <img
            src={previewUrl}
            alt="Preview"
            className="w-64 h-64 object-cover rounded"
          />
        </div>
      )}
    </div>
  );
}

export default App;
