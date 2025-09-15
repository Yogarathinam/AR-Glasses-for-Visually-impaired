# PSV905 - AR Navigation and Assistance for Visually Impaired Individuals  

### 🚀 Hackathon Project by Team Phoenix  
- **Problem Statement ID:** PSV905  
- **Domain:** Augmented/Virtual Reality  
- **College:** R.M.D. Engineering College  
- **Team Members:** Yogarathinam T L, Sanjay Kumar K, Saravan Kumaar R, Goutham V  

---

## 📌 Problem Statement  
Visually impaired individuals face significant challenges in safe mobility, especially in crowded public spaces.  
Traditional aids like canes or guide dogs have limitations, while smart glasses on the market are often **too costly, limited in features, and lack multilingual support**.  

**Our Goal:**  
To design an **affordable AR-based navigation system** that detects obstacles, recognizes landmarks, and provides real-time **audio guidance** for safer, independent mobility.  

---

## 💡 Proposed Solution  
- AR-based wearable system with **real-time obstacle detection**.  
- **Landmark recognition** (shops, bus stops, restrooms, etc.) using computer vision.  
- **Audio guidance** via TTS in multiple languages (English, Tamil, Telugu, etc.).  
- **OCR-based text reading** (e.g., reading signboards).  
- Low-cost hardware (Raspberry Pi / AR glasses + camera + earphones).  
- Seamless **voice interaction** for commands like:  
  - “Where am I?”  
  - “Read this board.”  
  - “Guide me to the bus stop.”  

---

## 🛠️ Technical Approach  

### Technologies Used
- **Programming Languages:** Python
- **Frameworks & Libraries:** OpenCV, YOLOv8, Tesseract OCR, Whisper STT, Edge TTS  
- **Hardware:** Raspberry Pi 3B+, Camera module, TWS earphones, AR glasses frame  

### Methodology (Flow)  
1. **Camera Feed** → Captured in real-time.  
2. **YOLOv8 Model** → Detects obstacles & people.  
3. **OCR (Tesseract)** → Reads text from signboards.  
4. **AI Assistant (Gemini API)** → Processes queries & generates responses.  
5. **TTS (Edge-TTS)** → Converts responses into natural speech.  
6. **Audio Output** → User receives navigation/audio guidance.  

---

## ✅ Feasibility & Viability  
- **Affordable**: Uses open-source frameworks + low-cost hardware.  
- **Scalable**: Can expand features like GPS integration & cloud AI.  
- **Challenges**: Real-time latency & outdoor lighting variations.  
- **Solutions**: Model optimization, edge computing, adaptive preprocessing.  

---

## 🌍 Impact & Social Relevance  
- Empowers **visually impaired individuals** with independent navigation.  
- Reduces reliance on costly assistive devices.  
- Promotes **inclusivity & accessibility** in smart city initiatives.  
- Supports **UN SDGs (Goal 10: Reduced Inequalities, Goal 11: Sustainable Cities & Communities)**.  

---

## 📊 Market Demand Analysis  
- **Global Need**: 285M visually impaired (WHO, 2023).  
- **Existing Solutions**: OrCam MyEye, Envision Glasses – effective but very expensive (~₹3,00,000+).  
- **Our Advantage**: Affordable, multilingual, AI-powered, scalable.  
- **Market Potential**: Huge demand in **India & developing countries** where cost-effective solutions are critical.  

---

## 📚 Research & References  
- WHO Global Report on Vision, 2023  
- Redmon et al., YOLOv8 Paper, 2022  
- OrCam MyEye Documentation  
- Tesseract OCR Documentation, 2023  
- OpenAI Whisper Documentation, 2023  
- Microsoft Edge-TTS API Docs  

---

## 🖼️ Demo / Prototype (To be added)  
- [ ] Upload demo video link / screenshots here  
- [ ] Flowchart & block diagram  

---

## 🦾 Future Scope  
- Full AR glasses prototype with built-in camera + speakers.  
- Indoor navigation using BLE beacons.  
- Cloud-based map integration for outdoor guidance.  
- Gesture recognition for hands-free control.  

---

## ✨ Ending Note  
> **"Empowering vision, enabling independence — because everyone deserves to navigate the world with confidence."**

---

## 👥 Team Phoenix  
- Yogarathinam T L  
- Sanjay Kumar K  
- Saravan Kumaar R  
- Goutham V  
