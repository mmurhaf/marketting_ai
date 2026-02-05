# Android Mobile App Conversion Prompt

## Project Overview
Convert the "Marketing AI" Python script into a native Android mobile application. Despite the project name, the application **does not use Generative AI (LLMs)**. It is a **Content Automation Tool** that scrapes images from a specific website (e.g., aleppogift.com), creates marketing reels/posts using local image processing, and saves them for the user.

The mobile version should focus on:
1.  Reading/Scraping content from the configured source.
2.  Assembling images into posts/videos locally.
3.  Gallery management.
4.  Totally Free & Offline-First logic.

## Requirements

### 1. Application Architecture
- **Language**: Kotlin (preferred) or Java
- **Minimum SDK**: API 24 (Android 7.0)
- **Target SDK**: API 34 (Android 14)
- **Architecture Pattern**: MVVM
- **No External Cloud Dependency**: All processing happens on the device.

### 2. Core Features to Implement

#### Content Automation (The "Browse & Create" Flow)
- **Web Reader (Scraper)**:
  - Fetches images/text from a target URL (configurable in Settings).
  - Background syncing (WorkManager) to check for new products/images.
  - Notifications when new content is found.
- **Content Assembler (Creator)**:
  - **Logic**: Replicates the Python `ContentCreator` class locally using Android libraries.
  - **Feature**: Select downloaded images -> Apply Text Overlay -> Generate Post/Reel.
  - **Templates**: Simple layouts (like the Python script's 1080x1080 crop).
  - **No AI**: Uses standard graphics drawing (Canvas/Bitmap) instead of AI generation.

#### Media Management
- **Gallery Module**:
  - Display generated images/assets
  - Image viewer with zoom capabilities
  - Local storage management
  - Delete and organize media files
  - Share images to other apps (excluding social media posting)



#### Settings & Configuration
- **Settings Module**:
  - Source Configuration (Target URL)
  - App preferences
  - Theme selection (Light/Dark mode)
  - Language settings
  - Cache management
  - About and help sections

#### Dashboard/Admin
- **Dashboard Module**:
  - Statistics overview (content created, images generated)
  - Quick action buttons
  - Recent activity feed
  - Storage usage indicators

### 3. Features to EXCLUDE
- ❌ Direct social media publishing (Facebook, Twitter, Instagram, LinkedIn, etc.)
- ❌ Social media account authentication/linking
- ❌ Scheduled posting features
- ❌ Social media analytics/insights
- ❌ Cross-platform posting capabilities

### 4. Technical Implementation Details

#### Backend & Connectivity
- **Web Scraping / API**:
  - Uses Retrofit/OkHttp to fetch HTML or JSON from the target website.
  - Parses content (using standard HTML parsers like Jsoup) to extract Image URLs and Titles.
- **Local Processing**:
  - All image manipulation (cropping, text overlay, video stitching) is done on the device CPU.
  - **Zero Cost**: No connection to OpenAI, Gemini, or any paid API.

#### Security
- Secure storage of the Target Website URL.
- Standard storage permissions.

### 5. Libraries & Dependencies

```gradle
dependencies {
    // Core Android
    implementation "androidx.core:core-ktx:1.12.0"
    implementation "androidx.appcompat:appcompat:1.6.1"
    implementation "com.google.android.material:material:1.11.0"
    
    // Jetpack Compose (if using)
    implementation platform("androidx.compose:compose-bom:2024.01.00")
    implementation "androidx.compose.ui:ui"
    implementation "androidx.compose.material3:material3"
    implementation "androidx.compose.ui:ui-tooling-preview"
    
    // Lifecycle & ViewModel
    implementation "androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0"
    implementation "androidx.lifecycle:lifecycle-runtime-ktx:2.7.0"
    
    // Navigation
    implementation "androidx.navigation:navigation-fragment-ktx:2.7.6"
    implementation "androidx.navigation:navigation-ui-ktx:2.7.6"
    
    // Networking
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
    implementation "com.squareup.okhttp3:okhttp:4.12.0"
    implementation "com.squareup.okhttp3:logging-interceptor:4.12.0"
    
    // Dependency Injection
    implementation "com.google.dagger:hilt-android:2.48"
    kapt "com.google.dagger:hilt-compiler:2.48"
    
    // Database
    implementation "androidx.room:room-runtime:2.6.1"
    implementation "androidx.room:room-ktx:2.6.1"
    kapt "androidx.room:room-compiler:2.6.1"
    
    // Image Loading
    implementation "io.coil-kt:coil:2.5.0"
    implementation "io.coil-kt:coil-compose:2.5.0"
    
    // Coroutines
    implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3"
    
    // Background & Scraping
    implementation "androidx.work:work-runtime-ktx:2.9.0"
    implementation "org.jsoup:jsoup:1.17.2" // For web scraping
    
    // DataStore (preferences)
    implementation "androidx.datastore:datastore-preferences:1.0.0"
}
```

### 6. App Structure

```
app/
├── src/main/
│   ├── java/com/sparkle/contentcreator/
│   │   ├── data/
│   │   │   ├── local/
│   │   │   │   ├── dao/
│   │   │   │   ├── database/
│   │   │   │   └── entities/
│   │   │   ├── remote/
│   │   │   │   ├── api/
│   │   │   │   ├── dto/
│   │   │   │   └── interceptors/
│   │   │   └── repository/
│   │   ├── di/  (Dependency Injection modules)
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   ├── repository/
│   │   │   └── usecase/
│   │   ├── presentation/
│   │   │   ├── common/  (shared composables/views)
│   │   │   ├── dashboard/
│   │   │   ├── content/
│   │   │   ├── gallery/
│   │   │   ├── settings/
│   │   │   └── MainActivity.kt
│   │   └── util/
│   ├── res/
│   │   ├── drawable/
│   │   ├── layout/  (if using XML)
│   │   ├── values/
│   │   │   ├── colors.xml
│   │   │   ├── strings.xml
│   │   │   ├── themes.xml
│   │   │   └── dimens.xml
│   │   └── xml/
│   │       └── network_security_config.xml
│   └── AndroidManifest.xml
└── build.gradle.kts
```

### 7. Key Screens & Navigation Flow

```
Splash Screen
    ↓
Dashboard (Main)
    ├── Content Creator
    │   ├── New Content
    │   ├── Edit Draft
    │   └── Content History
    ├── Gallery
    │   ├── Image Grid
    │   ├── Image Detail
    │   └── Share Options (system share)
    ├── History
    │   └── View Past Content
    └── Settings
        ├── Source URL Settings
        ├── Theme Settings
        ├── Cache Management
        ├── About
        └── Help
```

### 8. Google Play Store Requirements

#### App Metadata
- **App Name**: Sparkle Content Creator
- **Package Name**: com.sparkle.contentcreator
- **Version**: 1.0.0 (versionCode: 1)
- **Category**: Business / Productivity
- **Content Rating**: Everyone / PEGI 3

#### Required Assets
- App Icon (512x512 PNG)
- Feature Graphic (1024x500 PNG)
- Screenshots (minimum 2, up to 8):
  - Phone: 1080x1920 or higher
  - 7-inch Tablet (optional)
  - 10-inch Tablet (optional)
- Privacy Policy URL (required)
- App Description (short & full)

#### Store Listing Content
- **Short Description** (80 characters max)
- **Full Description** (4000 characters max)
- **Keywords/Tags** for ASO
- **What's New** section for updates

#### App Bundle
- Generate signed Android App Bundle (.aab)
- Configure ProGuard/R8 for release build
- Enable app signing by Google Play

### 9. Permissions Required

```xml
<manifest>
    <!-- Required Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <!-- Optional Permissions (request at runtime) -->
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" 
                     android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
                     android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
                     android:maxSdkVersion="28" />
    
    <!-- Android 13+ Permissions -->
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
</manifest>
```

### 10. Testing Requirements

#### Unit Tests
- Repository layer tests
- ViewModel tests
- Use case tests
- Minimum 70% code coverage

#### UI Tests
- Espresso or Compose UI tests
- Critical user flows
- Navigation tests

#### Manual Testing
- Test on multiple devices (different screen sizes)
- Test on different Android versions (API 24-34)
- Network error scenarios
- Offline functionality
- App lifecycle events

### 11. Build Configurations

```kotlin
// build.gradle.kts (app module)
android {
    namespace = "com.sparkle.contentcreator"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.sparkle.contentcreator"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-DEBUG"
        }
    }

    buildFeatures {
        compose = true  // if using Compose
        viewBinding = true  // if using XML
    }
}
```

### 12. Technical Considerations

- **HTML Parsing**: Use `Jsoup` (standard Java/Kotlin library) to replicate `BeautifulSoup` functionality.
- **Image Processing**: Use Android's native `Bitmap`, `Canvas`, and `Paint` classes to replicate `PIL.ImageDraw`.
- **Video Generation**: If "Reel" creation is needed, use `MediaCodec` or a lightweight wrapper like `ffmpeg-kit` (Android) to stitch images into video, similar to `moviepy`.
- **Background Sync**: Use `WorkManager` for daily checks (like the Python `schedule` library).

### 13. Pricing Model

- **Completely Free**: No API costs, no server costs. The app logic is self-contained.

### 14. Analytics & Crash Reporting

- Firebase Analytics for user behavior tracking
- Firebase Crashlytics for crash reporting
- Performance monitoring (Firebase Performance)
- Custom events for feature usage

### 15. Localization

- Support multiple languages (minimum: English)
- Externalize all strings
- RTL layout support if targeting RTL languages
- Date/time formatting based on locale

### 16. Accessibility

- Content descriptions for all interactive elements
- Support for TalkBack
- Minimum touch target size (48dp)
- Sufficient color contrast
- Text scaling support

### 17. Deliverables

1. **Complete Android Project**:
   - All source code organized in proper architecture
   - Build scripts and configuration files
   - README with setup instructions

2. **Documentation**:
   - Application usage guide
   - Architecture documentation
   - Developer onboarding guide

3. **Release Build**:
   - Signed AAB file ready for Play Store
   - Release notes
   - Version changelog

4. **Store Assets**:
   - All required graphics (icon, screenshots, feature graphic)
   - Store listing copy
   - Privacy policy document

5. **Testing Reports**:
   - Test coverage reports
   - Device compatibility matrix
   - Known issues/limitations

## Implementation Timeline Estimate

- Week 1-2: Project setup, architecture, and core infrastructure
- Week 3-4: Content creator module implementation
- Week 5-6: Gallery and media management
- Week 7: Settings and configuration
- Week 8: Dashboard and navigation
- Week 9-10: UI/UX polish, testing, bug fixes
- Week 11: Release preparation, store assets
- Week 12: Final testing, submission to Play Store

## Success Criteria

✅ App installs and runs on Android 7.0+ devices
✅ All core features functional without social media publishing
✅ Smooth UI with no ANR (Application Not Responding) issues
✅ No critical bugs or crashes
✅ Passes Google Play Store review guidelines
✅ App size under 50MB (initial download)
✅ App launches within 2 seconds
✅ Positive user experience with intuitive navigation

## Additional Notes

- Ensure compliance with Google Play policies
- Follow Material Design guidelines
- Optimize for battery consumption
- Implement proper error handling and user feedback
- Consider adding onboarding/tutorial for first-time users
- Plan for future updates and maintenance
- Keep the codebase clean and well-documented for maintainability

---

**Start Date**: [To be determined]
**Expected Completion**: 12 weeks from start
**Development Team**: Solo Developer (Author)
