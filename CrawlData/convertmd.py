# -*- coding: utf-8 -*-
import markdown
md = markdown.Markdown()
print (md.convert("# Lời dẫn\nNhư các bạn đã biết thì Android hiện tại đang chạy trên hàng tỷ thiết bị, từ điện thoại cao cấp, đồng hồ cho đến seatbacks trên máy bay. Tuy nhiên Google lại ko đưa ra bất cứ một chuẩn thiết kế nào dành cho developers. Các bạn có thể biết tới MVC, MVP, MVVM... và rất nhiều Architecture Pattern  khác nhưng tuyệt nhiên chúng ko phải là một chuẩn thiết kế được google khuyến cáo sử dụng. Từ trước đến giờ thì [Google](https://google.com) không hề suggest bất cứ gì về Architecture Components cả. Tuy nhiên tại sự kiện Google I/O 2017 vừa qua Google đã tung ra một chuẩn về thiết kế ứng dụng: **Architecture Components** \n- Persist Data\n- Manager Lifecycle\n- Make app modular\n- Avoid memory leak\n- Less boilerplate code\n\nTheo như Google công bố thì **Architecture Components**  gồm có 4 thành phần\n1. Room \n2. LiveData\n3. LifeCycle\n4. ViewModel\n\n\n# 1. Room\nRoom là một nó là một abstract layer cung cấp cách thức truy câp thao tác với dữ liệu trong cơ sở dữ liệu SQLite cực kì mạnh mẽ.\nCác bạn có thể theo dõi kĩ hơn cách sử dụng Room tại bài viết [này](https://viblo.asia/p/android-gioi-thieu-room-persistence-library-maGK7zne5j2) của mình để hiểu rõ hơn về Room và cách sử dụng nó nhé.\n\nĐể có thể tạo table thông qua Room các bạn cần định nghĩa một Plain Old Java Object (POJO) và đánh dấu POJO này với anotation @Entity \n```\nTrail.java\n\n@Entity\npublic class Trail {\n    public @PrimaryKey String id;\n    public String name;\n    public double kilometers;\n    public int difficulty;\n}\n```\nVới mỗi một POJO các bạn cần định nghĩa một Dao (Data access object)\n```\nTrailDao.java\n\n@Dao\npublic interface TrailDao {\n    @Insert(onConfict = IGNORE)\n    void insertTrail(Trail trail);\n    \n    @Query(\"SELECT * FROM Trail\")\n    List<Trail> findAllTrails();\n    \n    @Update(onConflict = REPLACE)\n    void updateTrail(Trail trail);\n    \n    @Query(\"DELETE FROM Trail\")\n    void deleteAll();\n    \n}\n```\n\nAnotation @Dao này đại diện cho câu lệnh SQLite sẽ tương tác với POJO mà các bạn đã định nghĩa ra ở trên.\nNhư các bạn đã thấy ở trên Room đã tự động convert data trong SQLite và trả về dữ liệu dưới dạng POJO ```List<Trail>```\nĐiều đặc biệt là Room verifies các câu lệnh SQLite của các bạn vào lúc compile chính vì vậy các bạn hoàn toàn có thể biết được mình viết câu lệnh có đúng hay không mà không cần phải chạy app và xem thử. Điều này SQLite Helper trước đó chưa thể thực hiện.\n![](https://viblo.asia/uploads/ef8d48ae-7210-4701-9c99-ff45cba4c5b7.png)\n\nOk các bạn đã có Room database rồi các bạn có thể sử dụng một architecture mới của Android là **LiveData** để có thể theo dõi sự thay đổi của dữ liệu trong database một cách realtime.\n\n# 2. LiveData\n![](https://viblo.asia/uploads/6ec7e920-e8b1-444f-b8f9-4a165d1e3feb.png)\n\nLiveData là một kiểu dữ liệu có thể quan sát được, nó có thể thông báo ngay lập tức khi có sự thay đổi về data vì vậy mà các bạn có thể update lại giao diện ngay lập tức. Ngoài ra nó hoàn toàn có thể nhận biết được lifecycle **(LifeCycler Aware - lát nói sau nha)**\nLiveData là một abstract class vì vậy các bạn hoàn toàn có thể extend LiveData hoặc đơn giản các bạn có thể sử dụng MutableLiveData class\n\n```\nMutableLiveData<String> dayOfWeek = new MutableLiveData<>();\ndayOfWeek.observer(this, data -> {\n    mTextView.setText(dayOfWeek.getValue() + \"is a good day for a hike\");\n    });\n ```\n ![](https://viblo.asia/uploads/af879175-87d5-40d4-a4c1-701c59eb7684.png)\n \n Và ngay khi các bạn update value của LiveData thì UI của bạn sẽ được update\n ```\n dayOfWeek.setValue(\"Friday\");\n ```\n ![](https://viblo.asia/uploads/2ee25fec-d073-43be-9dde-cb172cea7d64.png)\n \n Nhưng tuyệt vời hơn nữa rằng Room được xây dựng để hỗ trợ cho LiveData. Để sử dụng Room kết hợp với LiveData các bạn chỉ cần update DAO\n ```\nTrailDao.java\n\n@Dao\npublic interface TrailDao {\n    @Insert(onConfict = IGNORE)\n    void insertTrail(Trail trail);\n    \n//    @Query(\"SELECT * FROM Trail\")\n//    List<Trail> findAllTrails();\n//   Change List<Trail> to  LiveData<List<Trail>>\n\n    @Query(\"SELECT * FROM Trail\")\n    LiveData<List<Trail>> findAllTrails();\n    \n    @Update(onConflict = REPLACE)\n    void updateTrail(Trail trail);\n    \n    @Query(\"DELETE FROM Trail\")\n    void deleteAll();\n    \n}\n```\nRoom sẽ tạo ra một LiveData object để lắng nghe database, khi database có sự thay đổi LiveData sẽ thông báo và các bạn update ui\n```\ntrailsLiveData.observe(this, trails - > {\n    // Update UI, in this case a RecyclerView\n    mTrailsRecyclerAdapter.replaceItems(trails);\n    mTrailsRecyclerAdapter.notifyDataSetChanged();\n});\n````\nNhư mình định nghĩa ở trên thì LiveData là một lifecycle-aware component (Là component có thể nhận biết vòng đới)\nĐến đây thì chắc nhiều bạn sẽ tự hỏi lifecycle-aware component là gì? \nLifeCycle Aware Component\n- On Screen\n- Off Screen\n- Destroyed\nLiveData biết được khi nào activity đang on screen. off screen, hoặc destroy từ đó mà LiveData không gọi database update khi mà không có UI. Thật tối ưu phải không nào?\n\nCó 2 interface phục vụ cho việc này là **Lifecycle Owners**  và  **Lifecycle Observers**\n\n# 3. Lifecycle\nLifecycle là gì thì mình sẽ không giải thích thêm nữa nhé \n![](https://viblo.asia/uploads/0c2344c2-cebb-4a1a-bdae-37e735807a39.jpg)\nmình chỉ giải thích Lifecycle trong LiveData thôi\n\nLifecycle trong LiveData gồm có Lifecycle Owners và LifecyclObservers \n- **Lifecycle Owner** là những object có lifecycles như Activities, fragments \n- **LifecycleObservers**  lắng nghe Lifecycle Owner và thông báo khi lifecycle thay đổi.\n\nĐây là một ví dụ đơn giản về LiveData cũng là ví dụ về Lifecycle Observer\n```\nabstract public class LiveData<T> implements LifecycleObserver{\n    @OnLifecycleEvent(Lifecycle.Event.ON_START)\n    void startup(){\n    }\n\n    @OnLifecycleEvent(Lifecycle.Event.ON_STOP)\n    void cleanup(){\n    }\n}\n```\nNhững menthod mà được định nghĩa với anotaion @OnLifecycleEvent sẽ lắng nghe sự thay đổi của các Lifecycle Owner khi nó được khởi tạo hoặc destroy ...\n```\nDESTROYED, INITIALIZED, CREATED, STARTED, RESUMED\n```\nFlow cụ thể như sau \n![](https://viblo.asia/uploads/2e65b6a2-73c2-4034-a190-ca975abb9844.png)\n\nCác UI components lắng nghe LiveData, LiveData lắng nghe LifecycleOwners (Fragments/Activities)\n\nCó một vấn đề mà chắc hẳn là android developer các bạn ai cũng đã từng mắc phải đó là xử lý khi mà người dùng **\"XOAY MÀN HÌNH\"**\n![](https://viblo.asia/uploads/5c00bc0e-3930-4bdf-8d55-edf767d3dbde.png)\nVí dụ là khi màn hình bị xoay việc query data của các bạn lại diễn ra một lần nữa, thật là phiền phức phải không nào?\nGoogle đã nghe được lời đó của các con chiên developer, và ViewModel được ra đời.\n\n# 4. ViewModel\n![](https://viblo.asia/uploads/eeb4c280-3663-4c92-8240-e92613a7c720.png)\nView models là một objects cung cấp data cho UI components và luôn được giữ nguyên ngay cả khi thay đổi các thiết lập (ví dụ như screen  rotation)\nĐể tạo ra một ViewModel các bạn cần extend AndroidViewModel và put tất cả những data mà các bạn muốn sử dụng cho activity vào class đó \n```\npublic class TrailListViewModel extends AndroidViewModel {\n    private AppDatabasse mDatabase;\n    private LiveData<List<Trail>> trails;\n    \n    public TrailListViewModel(Application application){\n        super(application);\n        // AppDatabase is a Room database singleton\n        mDatabase = AppDatabase.getDb(getApplication());\n        trails = mDatabase.trailModel().findAllTrails();\n    }\n}\n```\n\nKhi các bạn đặt data vào trong ViewModel thì ứng dụng sẽ ko phải khởi tạo lại data khi activity được khởi tạo lại sau khi configuration thay đổi.\n\n# Tổng kết\nThông thường thì các ứng dụng Android sẽ được xây dựng như  sau\n![](https://viblo.asia/uploads/cb49964c-d791-496b-b10f-12cedd9282ba.png)\n\nTrên đây là phần trình bày của mình về Architecture Components\nCác bạn có thể tham khảo thêm về Architecture Components tại [đây](https://developer.android.com/topic/libraries/architecture/guide.html) nhé\nDemo mà mình thực hiện tại [đây](https://github.com/DoanVanToan/ArchitectureComponents)\n\nCám ơn các bạn đã đón đọc và chúc các bạn học tốt!"))