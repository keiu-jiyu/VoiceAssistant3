import React, { useState, useEffect, useRef } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useTracks,
  useRoomContext,
  useLocalParticipant,
} from '@livekit/components-react';
import '@livekit/components-styles';
import { Track } from 'livekit-client';

const serverUrl = process.env.REACT_APP_LIVEKIT_URL || 'ws://localhost:7880';
const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function App() {
  const [token, setToken] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authToken, setAuthToken] = useState('');

  // 检查是否已登录
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      setAuthToken(savedToken);
      setIsAuthenticated(true);
    }
  }, []);

  // 获取 LiveKit Token（登录后）
  useEffect(() => {
    if (!isAuthenticated || !authToken) return;

    const fetchLiveKitToken = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/token`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (!response.ok) {
          throw new Error('获取 LiveKit Token 失败');
        }
        
        const data = await response.json();
        console.log('✅ 获取到 token:', data.token);
        setToken(data.token);
      } catch (error) {
        console.error('❌ 获取token失败:', error);
        alert('获取连接令牌失败，请重新登录');
        handleLogout();
      }
    };

    fetchLiveKitToken();
  }, [isAuthenticated, authToken]);

  const handleLoginSuccess = (token) => {
    console.log('✅ 登录成功，保存认证 token');
    setAuthToken(token);
    setIsAuthenticated(true);
    localStorage.setItem('auth_token', token);
  };

  const handleLogout = () => {
    console.log('👋 退出登录');
    setAuthToken('');
    setIsAuthenticated(false);
    setToken('');
    setIsConnected(false);
    localStorage.removeItem('auth_token');
  };

  // 如果未登录，显示登录表单
  if (!isAuthenticated) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />;
  }

  // 登录后显示原有界面
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h1>🎙️ Voice Assistant</h1>
        <button
          onClick={handleLogout}
          style={{
            padding: '8px 16px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          退出登录
        </button>
      </div>
      
      <p style={{ fontSize: '12px', color: '#666' }}>
        LiveKit URL: {serverUrl}
      </p>
      
      {token ? (
        <LiveKitRoom
          token={token}
          serverUrl={serverUrl}
          connect={true}
          audio={true}
          video={false}
          onConnected={() => {
            console.log('✅ 已连接到房间');
            setIsConnected(true);
          }}
          onDisconnected={() => {
            console.log('❌ 已断开连接');
            setIsConnected(false);
          }}
          onError={(error) => {
            console.error('❌ LiveKit 连接错误:', error);
          }}
        >
          <div>
            {isConnected ? (
              <p style={{ color: 'green', fontWeight: 'bold' }}>
                ✓ 已连接到 LiveKit - 请开始说话
              </p>
            ) : (
              <p style={{ color: 'orange' }}>⏳ 连接中...</p>
            )}
          </div>

          <RoomAudioRenderer />
          <MicrophoneManager />
          <RoomStatus />
          <AudioManager />
        </LiveKitRoom>
      ) : (
        <p>⏳ 正在获取token...</p>
      )}
    </div>
  );
}

// 登录表单组件
function LoginForm({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      console.log('🔐 开始登录...');
      
      const response = await fetch(`${backendUrl}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '登录失败');
      }

      const data = await response.json();
      console.log('✅ 登录成功');
      onLoginSuccess(data.access_token);
      
    } catch (err) {
      console.error('❌ 登录失败:', err);
      setError(err.message || '登录失败，请检查邮箱和密码');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>🎙️ Voice Assistant</h1>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              邮箱
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '5px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
              placeholder="1111@gmail.com"
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              密码
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '5px',
                fontSize: '16px',
                boxSizing: 'border-box'
              }}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div style={{
              padding: '10px',
              marginBottom: '20px',
              backgroundColor: '#fee',
              color: '#c33',
              borderRadius: '5px',
              border: '1px solid #fcc'
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: isLoading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? '登录中...' : '登录'}
          </button>
        </form>

        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#f0f8ff',
          borderRadius: '5px',
          fontSize: '14px'
        }}>
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>测试账号：</p>
          <p style={{ margin: '5px 0' }}>邮箱: test@example.com</p>
          <p style={{ margin: '5px 0' }}>密码: password123</p>
        </div>
      </div>
    </div>
  );
}

function MicrophoneManager() {
  const { localParticipant } = useLocalParticipant();
  const [micEnabled, setMicEnabled] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!localParticipant) return;

    const publishMicrophone = async () => {
      try {
        console.log('🎤 请求麦克风权限...');
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioDevices = devices.filter(d => d.kind === 'audioinput');
        console.log('🎧 可用音频设备:', audioDevices);

        await localParticipant.setMicrophoneEnabled(true);
        console.log('✅ 麦克风已启用');
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const micTrack = localParticipant.getTrackPublication(Track.Source.Microphone);
        console.log('📡 麦克风轨道:', {
          sid: micTrack?.trackSid,
          isMuted: micTrack?.isMuted,
          isEnabled: micTrack?.isEnabled,
          track: micTrack?.track
        });

        if (micTrack?.track) {
          console.log('✅ 麦克风轨道已成功发布!');
          setMicEnabled(true);
        } else {
          console.error('❌ 麦克风轨道未发布');
          setError('麦克风轨道未发布');
        }
      } catch (err) {
        console.error('❌ 发布麦克风失败:', err);
        setError(err.message);
      }
    };

    publishMicrophone();
  }, [localParticipant]);

  return (
    <div style={{ 
      margin: '10px 0', 
      padding: '10px', 
      backgroundColor: micEnabled ? '#e8f5e9' : '#fff3e0', 
      borderRadius: '5px' 
    }}>
      <p>
        🎤 麦克风状态: {
          micEnabled 
            ? <span style={{ color: 'green', fontWeight: 'bold' }}>✓ 已启用</span>
            : <span style={{ color: 'orange' }}>⏳ 正在启用...</span>
        }
      </p>
      {error && (
        <p style={{ color: 'red', fontSize: '12px' }}>
          ⚠️ 错误: {error}
        </p>
      )}
    </div>
  );
}

function RoomStatus() {
  const room = useRoomContext();
  const [participantCount, setParticipantCount] = useState(0);

  useEffect(() => {
    if (!room) return;

    const updateCount = () => {
      const count = room.remoteParticipants.size;
      setParticipantCount(count);
      console.log('👥 远程参与者数量:', count);
      console.log('🎤 本地麦克风状态:', room.localParticipant.isMicrophoneEnabled);
      
      room.remoteParticipants.forEach((participant) => {
        console.log('👤 远程参与者:', participant.identity);
      });
    };

    updateCount();
    room.on('participantConnected', (participant) => {
      console.log('✅ 新参与者加入:', participant.identity);
      updateCount();
    });
    room.on('participantDisconnected', (participant) => {
      console.log('❌ 参与者离开:', participant.identity);
      updateCount();
    });

    return () => {
      room.off('participantConnected', updateCount);
      room.off('participantDisconnected', updateCount);
    };
  }, [room]);

  return (
    <div style={{ 
      margin: '10px 0', 
      padding: '10px', 
      backgroundColor: '#f5f5f5', 
      borderRadius: '5px' 
    }}>
      <p>👤 本地用户: {room?.localParticipant.identity || '未知'}</p>
      <p>👥 远程参与者: {participantCount}</p>
      <p>🎤 麦克风: {
        room?.localParticipant.isMicrophoneEnabled 
          ? <span style={{ color: 'green' }}>已启用 ✓</span>
          : <span style={{ color: 'red' }}>已禁用 ✗</span>
      }</p>
    </div>
  );
}

function AudioManager() {
  const tracks = useTracks([
    { source: Track.Source.Microphone, withPlaceholder: false },
    { source: Track.Source.Unknown, withPlaceholder: false },
  ]);
  
  const audioRefs = useRef(new Map());
  const containerRef = useRef(null);

  useEffect(() => {
    console.log('🔍 检测到的轨道数量:', tracks.length);

    tracks.forEach((trackReference) => {
      const { publication, participant } = trackReference;
      
      console.log('📡 轨道信息:', {
        trackSid: publication.trackSid,
        source: Track.Source[publication.source],
        kind: publication.kind,
        participant: participant.identity,
        isLocal: participant.isLocal,
        isMuted: publication.isMuted,
        isSubscribed: publication.isSubscribed,
      });

      if (participant.isLocal) {
        console.log('⏭️ 跳过本地轨道 (自己的声音)');
        return;
      }

      if (publication.kind === Track.Kind.Audio) {
        const track = publication.track;
        
        if (track) {
          if (!audioRefs.current.has(publication.trackSid)) {
            const audioElement = document.createElement('audio');
            audioElement.autoplay = true;
            audioElement.playsInline = true;
            audioElement.volume = 1.0;

            if (containerRef.current) {
              containerRef.current.appendChild(audioElement);
            }
            
            audioRefs.current.set(publication.trackSid, audioElement);
            console.log('🎵 创建新的 audio 元素，trackSid:', publication.trackSid);
          }

          const element = audioRefs.current.get(publication.trackSid);
          track.attach(element);
          
          const playAudio = async () => {
            try {
              await element.play();
              console.log('✅ AI音频开始播放, trackSid:', publication.trackSid);
            } catch (error) {
              console.warn('⚠️ 自动播放被阻止:', error);
              console.log('💡 提示：请点击页面任意位置以允许音频播放');
            }
          };
          
          playAudio();
        } else {
          console.warn('⚠️ 轨道对象为空');
        }
      }
    });

    return () => {
      tracks.forEach((trackReference) => {
        const { publication } = trackReference;
        const track = publication?.track;
        if (track) {
          const element = audioRefs.current.get(publication.trackSid);
          if (element) {
            track.detach(element);
            element.remove();
            audioRefs.current.delete(publication.trackSid);
            console.log('🗑️ 清理音频元素:', publication.trackSid);
          }
        }
      });
    };
  }, [tracks]);

  return (
    <div>
      <div ref={containerRef} style={{ display: 'none' }} />
      
      <div style={{ 
        margin: '10px 0', 
        padding: '10px', 
        backgroundColor: '#e3f2fd', 
        borderRadius: '5px' 
      }}>
        <h3>🎵 音频轨道 ({tracks.length})</h3>
        {tracks.length === 0 ? (
          <p style={{ color: '#999', fontSize: '12px' }}>暂无音频轨道</p>
        ) : (
          tracks.map((trackRef) => (
            <div 
              key={trackRef.publication.trackSid} 
              style={{ 
                fontSize: '12px', 
                marginBottom: '5px',
                padding: '5px',
                backgroundColor: trackRef.participant.isLocal ? '#fff9c4' : '#c8e6c9',
                borderRadius: '3px'
              }}
            >
              • <strong>{trackRef.participant.identity}</strong> - 
              {Track.Source[trackRef.publication.source]} - 
              {trackRef.publication.kind}
              {trackRef.participant.isLocal && ' 🎤 (本地)'}
              {!trackRef.participant.isLocal && ' 🤖 (远程)'}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;