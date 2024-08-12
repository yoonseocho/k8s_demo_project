import React, { createContext, useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './Login';
import Score from './Score';
import './App.css';

import axios from 'axios';

axios.defaults.transformResponse = [
  (data) => {
    try {
      return JSON.parse(data);
    } catch (error) {
      return data;
    }
  },
];

// UserContext 생성
export const UserContext = createContext();

function App() {
  const [user, setUser] = useState(null);

  return (
    <Router>
      <UserContext.Provider value={{ user, setUser }}>
        <div className="App">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/score" element={<Score />} />
          </Routes>
        </div>
      </UserContext.Provider>
    </Router>
  );
}

export default App;
