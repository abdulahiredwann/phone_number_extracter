import React, { useState, useEffect } from "react";
import axios from "axios";
import { useWebSocket } from "../hooks/useWebSocket";

const Upload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState("");
  const [currentFrame, setCurrentFrame] = useState(0);
  const [totalFrames, setTotalFrames] = useState(0);

  // WebSocket connection
  const { isConnected, lastMessage, error: wsError } = useWebSocket(taskId);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case "progress_update":
          setProgress(lastMessage.progress || 0);
          setCurrentFrame(lastMessage.current_frame || 0);
          setTotalFrames(lastMessage.total_frames || 0);
          setCurrentMessage(lastMessage.message || "");
          break;
        case "task_completed":
          setProgress(100);
          setCurrentMessage(lastMessage.message || "Processing completed!");
          setUploading(false);
          // Fetch results
          if (taskId) {
            fetchResults(taskId);
          }
          break;
        case "task_failed":
          setError(lastMessage.error_message || "Processing failed");
          setUploading(false);
          break;
      }
    }
  }, [lastMessage, taskId]);

  const fetchResults = async (taskId: string) => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/task/${taskId}/results`
      );
      setResults(response.data);
    } catch (err: any) {
      console.error("Error fetching results:", err);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = ["video/mp4", "video/avi", "video/mov", "video/mkv"];
      if (!allowedTypes.includes(file.type)) {
        setError("Please select a valid video file (MP4, AVI, MOV, MKV)");
        return;
      }

      // Validate file size (max 100MB)
      const maxSize = 100 * 1024 * 1024; // 100MB
      if (file.size > maxSize) {
        setError("File size must be less than 100MB");
        return;
      }

      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a video file");
      return;
    }

    setUploading(true);
    setError(null);
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("video", selectedFile);

      console.log("🚀 Starting video upload...");
      console.log("📁 File:", selectedFile.name);

      const response = await axios.post(
        "http://localhost:8000/api/upload-video",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 30000, // 30 seconds timeout for upload
        }
      );

      console.log("✅ Upload successful:", response.data);
      setTaskId(response.data.task_id);
      setProgress(0);
      setCurrentMessage("Video uploaded successfully. Processing started...");
    } catch (err: any) {
      console.error("❌ Upload failed:", err);
      setError(err.response?.data?.detail || err.message || "Upload failed");
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            📹 Video Phone Number Extractor
          </h1>

          <div className="space-y-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Video File
              </label>
              <input
                type="file"
                accept="video/mp4,video/avi,video/mov,video/mkv"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                disabled={uploading}
              />
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {selectedFile.name} (
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              )}
            </div>

            {/* Upload Button */}
            <div className="text-center">
              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                className={`px-8 py-3 rounded-lg font-semibold text-white transition-colors ${
                  !selectedFile || uploading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {uploading ? (
                  <span className="flex items-center justify-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    {uploading && !taskId
                      ? "Uploading..."
                      : "Processing Video..."}
                  </span>
                ) : (
                  "🚀 Extract Phone Numbers"
                )}
              </button>
            </div>

            {/* WebSocket Status */}
            {taskId && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-700">
                    WebSocket Status:
                  </span>
                  <span
                    className={`text-sm ${
                      isConnected ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {isConnected ? "🟢 Connected" : "🔴 Disconnected"}
                  </span>
                </div>
                {wsError && (
                  <p className="text-sm text-red-600 mb-2">{wsError}</p>
                )}
              </div>
            )}

            {/* Progress Bar */}
            {uploading && taskId && (
              <div className="bg-white border border-gray-200 rounded-md p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  📊 Processing Progress
                </h3>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>

                {/* Frame Progress */}
                {totalFrames > 0 && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Frames</span>
                      <span>
                        {currentFrame} / {totalFrames}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${(currentFrame / totalFrames) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Current Message */}
                {currentMessage && (
                  <div className="text-sm text-gray-700">
                    <span className="font-medium">Status:</span>{" "}
                    {currentMessage}
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-red-400"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <div className="mt-2 text-sm text-red-700">{error}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {results && (
              <div className="bg-green-50 border border-green-200 rounded-md p-6">
                <h3 className="text-lg font-semibold text-green-800 mb-4">
                  ✅ Processing Complete!
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-green-700">
                      Status:
                    </span>
                    <span className="text-sm text-green-600">
                      {results.status}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-green-700">
                      Total Phone Numbers Found:
                    </span>
                    <span className="text-sm text-green-600 font-bold">
                      {results.total_phone_numbers}
                    </span>
                  </div>

                  {results.phone_numbers &&
                    results.phone_numbers.length > 0 && (
                      <div className="mt-4">
                        <h4 className="text-md font-semibold text-green-800 mb-2">
                          📞 Found Phone Numbers:
                        </h4>
                        <div className="space-y-2">
                          {results.phone_numbers.map(
                            (phone: any, index: number) => (
                              <div
                                key={index}
                                className="bg-white p-3 rounded border border-green-200"
                              >
                                <div className="flex justify-between items-start">
                                  <div>
                                    <p className="font-semibold text-gray-900">
                                      {phone.e164_number}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                      {phone.national_number}
                                    </p>
                                  </div>
                                  <div className="text-right text-sm text-gray-500">
                                    <p>
                                      First seen: {phone.first_seen_seconds}s
                                    </p>
                                    <p>Frames: {phone.frame_count}</p>
                                  </div>
                                </div>
                                {phone.raw_text_examples && (
                                  <p className="text-xs text-gray-500 mt-2">
                                    Examples: {phone.raw_text_examples}
                                  </p>
                                )}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
