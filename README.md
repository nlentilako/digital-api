# Digital Orchestrator API

A production-ready Digital Services (VTU) API built with Clean Modular Digital Orchestrator Architecture.

## 🚀 Features

### 🔐 Authentication & Roles
- Custom User model with extended fields
- Role-based access control (Admin, Agent, User, API Reseller)
- JWT authentication (access + refresh tokens)
- Rate limiting per role

### 📡 Digital Products
- Service Types: Data Bundles, Airtime, WAEC Pins, School Vouchers
- Network Providers: MTN, Vodafone, AirtelTigo
- Enable/disable services
- Dynamic pricing per role
- Network brand metadata

### 🔁 Purchase Orchestration Flow
1. Validate user & permissions
2. Validate wallet balance
3. Lock wallet
4. Select provider via `provider_factory`
5. Execute transaction
6. Handle provider response
7. Confirm / rollback
8. Log transaction

### 🔌 Provider Abstraction
- All providers implement `BaseProvider`
- Swap providers without touching core logic
- Built-in retry & failover support

### 💰 Wallet System
- Wallet funding
- Debit & credit operations
- Transaction history
- Auto-rollback on failure

### 🔑 API Reseller System
- API key generation
- Per-key pricing
- Usage limits
- IP whitelisting
- Usage analytics

### 📊 Admin Dashboard Support
- User management
- Agent pricing configuration
- Service enable/disable
- Revenue reports
- Failed transaction tracking
