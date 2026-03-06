
import React, { useState, useEffect } from 'react';
import axios from 'axios';

/**
 * 공동구매 대시보드
 * 
 * 기능:
 * - 오늘의 핫딜
 * - 우리 마을 공동구매
 * - 카테고리별 공동구매
 * - 진행 상황 실시간 업데이트
 */
const GroupPurchaseDashboard = () => {
  const [hotDeals, setHotDeals] = useState([]);
  const [villagePurchases, setVillagePurchases] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);

  // API 베이스 URL
  const API_BASE = '/api/group-purchase';

  // 핫딜 조회
  useEffect(() => {
    const fetchHotDeals = async () => {
      try {
        const response = await axios.get(`${API_BASE}/hot-deals`);
        setHotDeals(response.data.hot_deals);
      } catch (error) {
        console.error('핫딜 조회 실패:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHotDeals();
    
    // 30초마다 자동 갱신
    const interval = setInterval(fetchHotDeals, 30000);
    return () => clearInterval(interval);
  }, []);

  // 우리 마을 공동구매 조회
  useEffect(() => {
    const fetchVillagePurchases = async () => {
      const villageId = localStorage.getItem('user_village') || '강원도 인제군';
      
      try {
        const response = await axios.get(`${API_BASE}/village/${encodeURIComponent(villageId)}`);
        setVillagePurchases(response.data.purchases);
      } catch (error) {
        console.error('마을 공동구매 조회 실패:', error);
      }
    };

    fetchVillagePurchases();
  }, []);

  // 공동구매 참여
  const joinCampaign = async (campaignId, quantity = 1) => {
    const userId = localStorage.getItem('user_id') || 'guest';
    
    try {
      const response = await axios.post(`${API_BASE}/join`, {
        campaign_id: campaignId,
        user_id: userId,
        quantity: quantity
      });

      if (response.data.success) {
        alert('공동구매 참여 완료!');
        // 핫딜 다시 조회 (진행률 업데이트)
        window.location.reload();
      } else {
        alert(response.data.message);
      }
    } catch (error) {
      console.error('참여 실패:', error);
      alert('참여 중 오류가 발생했습니다.');
    }
  };

  // 진행률 계산
  const calculateProgress = (current, target) => {
    return Math.min(Math.round((current / target) * 100), 100);
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  return (
    <div className="group-purchase-dashboard">
      {/* 헤더 */}
      <header className="dashboard-header">
        <h1>🌾 Mulberry 공동구매</h1>
        <p>식품사막화 지역 생산품을 함께 구매해요!</p>
      </header>

      {/* 오늘의 핫딜 */}
      <section className="hot-deals-section">
        <h2>🔥 오늘의 핫딜</h2>
        
        <div className="deals-grid">
          {hotDeals.map((deal) => (
            <div key={deal.campaign_id} className="deal-card">
              {/* 상품 이미지 */}
              <div className="deal-image">
                <img 
                  src={deal.image_urls?.[0] || '/placeholder.jpg'} 
                  alt={deal.name} 
                />
                
                {/* 할인율 배지 */}
                <div className="discount-badge">
                  {deal.discount_rate}% 할인
                </div>
              </div>

              {/* 상품 정보 */}
              <div className="deal-info">
                <h3>{deal.name}</h3>
                <p className="producer-location">
                  📍 {deal.producer_location}
                </p>

                {/* 가격 */}
                <div className="price-info">
                  <span className="original-price">
                    {deal.original_price.toLocaleString()}원
                  </span>
                  <span className="group-price">
                    {deal.group_price.toLocaleString()}원
                  </span>
                </div>

                {/* 진행 상황 */}
                <div className="progress-section">
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar" 
                      style={{
                        width: `${calculateProgress(
                          deal.current_participants, 
                          deal.min_participants
                        )}%`
                      }}
                    />
                  </div>
                  
                  <div className="progress-text">
                    👥 {deal.current_participants}/{deal.min_participants}명
                    ({calculateProgress(
                      deal.current_participants, 
                      deal.min_participants
                    )}%)
                  </div>
                </div>

                {/* 참여 버튼 */}
                <button 
                  className="join-button"
                  onClick={() => joinCampaign(deal.campaign_id)}
                >
                  지금 참여하기
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 우리 마을 공동구매 */}
      <section className="village-section">
        <h2>👥 우리 마을 공동구매</h2>
        
        <div className="village-purchases">
          {villagePurchases.map((purchase) => (
            <div key={purchase.campaign_id} className="village-card">
              <h3>{purchase.name}</h3>
              <p>📍 {purchase.producer_location}</p>
              <p>💰 {purchase.group_price.toLocaleString()}원</p>
              
              <button onClick={() => joinCampaign(purchase.campaign_id)}>
                참여하기
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* 카테고리별 공동구매 */}
      <section className="category-section">
        <h2>📦 카테고리별 공동구매</h2>
        
        <div className="category-tabs">
          <button 
            className={selectedCategory === 'all' ? 'active' : ''}
            onClick={() => setSelectedCategory('all')}
          >
            전체
          </button>
          <button 
            className={selectedCategory === 'agricultural' ? 'active' : ''}
            onClick={() => setSelectedCategory('agricultural')}
          >
            농산물
          </button>
          <button 
            className={selectedCategory === 'seafood' ? 'active' : ''}
            onClick={() => setSelectedCategory('seafood')}
          >
            수산물
          </button>
          <button 
            className={selectedCategory === 'processed' ? 'active' : ''}
            onClick={() => setSelectedCategory('processed')}
          >
            가공식품
          </button>
        </div>
      </section>
    </div>
  );
};

export default GroupPurchaseDashboard;
