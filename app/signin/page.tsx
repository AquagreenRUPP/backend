"use client";

import axios from "axios";
import React, { useState } from "react";
import { useRouter } from "next/navigation";

const Login = () => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/sign_in", {
        phone_number: phoneNumber,
        password: password,
      });

      // Save tokens to localStorage
      const { access_token } = response.data.result;
      if (access_token) {
        localStorage.setItem("access_token", access_token);

        // Redirect to the dashboard
        setResponseMessage("Login successful! Redirecting...");
        router.push("/dashboard");
      } else {
        setResponseMessage("Login successful, but no token received.");
      }
    } catch (error) {
      setResponseMessage(
        `Error: ${error.response?.data?.detail || "Something went wrong"}`
      );
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto", textAlign: "center" }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        <div>
          <label>Phone Number:</label>
          <input
            type="text"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            required
            style={{ width: "100%", padding: "8px", margin: "5px 0" }}
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: "8px", margin: "5px 0" }}
          />
        </div>
        <button type="submit" style={{ padding: "10px", backgroundColor: "#0070f3", color: "white", border: "none", borderRadius: "5px", cursor: "pointer" }}>
          Login
        </button>
      </form>
      {responseMessage && <p style={{ marginTop: "10px", color: "black" }}>{responseMessage}</p>}
    </div>
  );
};

export default Login;
