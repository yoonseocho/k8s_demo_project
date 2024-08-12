import React, { useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { UserContext } from './App';  // App.js에서 export한 UserContext를 import

function Score() {
  const { user } = useContext(UserContext);
  const [dbScore, setDbScore] = useState(null);
  const [newScore, setNewScore] = useState('');

  console.log('Username:', user?.username);  // 디버깅을 위한 로그

  const fetchScore = useCallback(async () => {
    if (!user?.username) return;

    try {
      const response = await axios.get(`api/get_score/${user.username}`);
      console.log('Fetch score response:', response.data);
      if (response.data.success) {
        setDbScore(response.data.score);
      } else {
        console.error('점수 가져오기 실패:', response.data.message);
      }
    } catch (error) {
      console.error('점수 가져오기 오류:', error.response?.data || error.message);
    }
  }, [user?.username]);

  useEffect(() => {
    fetchScore();
  }, [fetchScore]);

  const handleUpdate = async () => {
    if (!newScore) {
      alert('업데이트할 점수를 입력해주세요.');
      return;
    }

    if (!user?.username) {
      alert('사용자 정보가 없습니다. 다시 로그인해주세요.');
      return;
    }

    try {
      const response = await axios.post('api/update_score', {
        username: user.username,
        score: parseInt(newScore)
      });
      console.log('Update score response:', response.data);

      if (response.data.success) {
        setDbScore(response.data.new_score);
        setNewScore('');
        alert('점수가 업데이트되었습니다.');
      } else {
        alert('점수 업데이트에 실패했습니다: ' + response.data.message);
      }
    } catch (error) {
      console.error('점수 업데이트 실패:', error.response?.data || error.message);
      alert('점수 업데이트 실패: ' + (error.response?.data?.message || error.message));
    }
  };

  return (
    <div>
      <h2>현재 DB에 저장된 점수: {dbScore !== null ? dbScore : '불러오는 중...'}</h2>
      <input
        type="number"
        value={newScore}
        onChange={(e) => setNewScore(e.target.value)}
        placeholder="새로운 점수 입력"
        style={{ padding: '10px', margin: '10px', width: '200px' }}
      />
      <button onClick={handleUpdate}>점수 업데이트</button>
    </div>
  );
};

export default Score;
