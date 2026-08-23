from __future__ import annotations

from yt_dlp_plugins.extractor.radiko_dependencies import protobug

if protobug:

    class EpisodeOrder(protobug.Enum, strict=False):
        START_AT_ASC = 0
        START_AT_DESC = 1

    class EpisodePlaybackStatusFilter(protobug.Enum, strict=False):
        ALL = 0
        UNPLAYED = 1
        STARTED = 2

    class GenreKind(protobug.Enum, strict=False):
        UNKNOWN = 0
        PERSONALITY = 1
        PROGRAM = 2

    class PodcastStationType(protobug.Enum, strict=False):
        PODCAST_STATION_TYPE_UNKNOWN = 0
        PODCAST_STATION_TYPE_RADIO = 1
        PODCAST_STATION_TYPE_RADIO_AFFILIATED = 2
        PODCAST_STATION_TYPE_OTHER = 3

    class ProgramSource(protobug.Enum, strict=False):
        UNKNOWN_SOURCE = 0
        LIVE = 1
        TIME_FREE = 2

    class TypeDayOfWeek(protobug.Enum, strict=False):
        DAY_OF_WEEK_UNSPECIFIED = 0
        MONDAY = 1
        TUESDAY = 2
        WEDNESDAY = 3
        THURSDAY = 4
        FRIDAY = 5
        SATURDAY = 6
        SUNDAY = 7

    @protobug.message
    class Image:
        url: protobug.String | None = protobug.field(1, default=None)
        genre: protobug.String | None = protobug.field(2, default=None)
        width: protobug.Int32 | None = protobug.field(3, default=None)
        height: protobug.Int32 | None = protobug.field(4, default=None)
        sizeType: protobug.String | None = protobug.field(5, default=None)

    @protobug.message
    class Actor:
        key: protobug.String | None = protobug.field(1, default=None)
        name: protobug.String | None = protobug.field(2, default=None)
        nameKana: protobug.String | None = protobug.field(3, default=None)
        nameEnglish: protobug.String | None = protobug.field(4, default=None)
        images: list[Image] = protobug.field(5, default_factory=list)
        description: protobug.String | None = protobug.field(6, default=None)
        information: protobug.String | None = protobug.field(7, default=None)

    @protobug.message
    class Any:
        typeUrl: protobug.String | None = protobug.field(1, default=None)
        value: protobug.Bytes | None = protobug.field(2, default=None)

    @protobug.message
    class Article:
        id: protobug.Int32 | None = protobug.field(1, default=None)
        title: protobug.String | None = protobug.field(2, default=None)
        publisherName: protobug.String | None = protobug.field(3, default=None)
        imageUrl: protobug.String | None = protobug.field(4, default=None)
        url: protobug.String | None = protobug.field(5, default=None)

    @protobug.message
    class FieldViolation:
        field: protobug.String | None = protobug.field(1, default=None)
        description: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class BadRequest:
        fieldViolations: list[FieldViolation] = protobug.field(1, default_factory=list)

    @protobug.message
    class BatchDeletePlayHistoriesRequest:
        ids: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class BatchDeletePlayHistoriesResponse:
        pass

    @protobug.message
    class BatchDeletePodcastEpisodePlayHistoriesRequest:
        ids: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class BatchGetActorsRequest:
        actorKeys: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class BatchGetActorsResponse:
        actors: list[Actor] = protobug.field(1, default_factory=list)

    @protobug.message
    class BatchGetFollowingItemsRequest:
        followingItemIds: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class Timestamp:
        seconds: protobug.Int64 | None = protobug.field(1, default=None)
        nanos: protobug.Int32 | None = protobug.field(2, default=None)

    @protobug.message
    class FollowingItem:
        id: protobug.String | None = protobug.field(1, default=None)
        backgroundImageUrl: protobug.String | None = protobug.field(4, default=None)
        actorId: protobug.String | None = protobug.field(5, default=None)
        createdAt: Timestamp | None = protobug.field(6, default=None)
        rSeasonId: protobug.String | None = protobug.field(7, default=None)
        rSeasonName: protobug.String | None = protobug.field(8, default=None)
        stationId: protobug.String | None = protobug.field(9, default=None)
        dow: TypeDayOfWeek | None = protobug.field(10, default=None)
        startAtTime: protobug.String | None = protobug.field(11, default=None)
        userFollowingItemDowId: protobug.String | None = protobug.field(12, default=None)
        backgroundImageSquareUrl: protobug.String | None = protobug.field(13, default=None)

    @protobug.message
    class BatchGetFollowingItemsResponse:
        followingItems: list[FollowingItem] = protobug.field(1, default_factory=list)

    @protobug.message
    class BatchGetNoaItemsRequest:
        noaIds: protobug.String | None = protobug.field(1, default=None)
        shopIds: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class NoaItem:
        id: protobug.String | None = protobug.field(1, default=None)
        noaId: protobug.String | None = protobug.field(2, default=None)
        programTitle: protobug.String | None = protobug.field(3, default=None)
        url: protobug.String | None = protobug.field(4, default=None)
        imageUrl: protobug.String | None = protobug.field(5, default=None)
        imageLargeUrl: protobug.String | None = protobug.field(6, default=None)
        artist: protobug.String | None = protobug.field(7, default=None)
        title: protobug.String | None = protobug.field(8, default=None)
        amazonLink: protobug.String | None = protobug.field(9, default=None)
        programStationId: protobug.String | None = protobug.field(10, default=None)
        programStartAt: Timestamp | None = protobug.field(11, default=None)
        noaPlayedAt: Timestamp | None = protobug.field(12, default=None)
        itunesLink: protobug.String | None = protobug.field(13, default=None)
        recochokuLink: protobug.String | None = protobug.field(14, default=None)
        createdAt: Timestamp | None = protobug.field(15, default=None)
        shopId: protobug.String | None = protobug.field(16, default=None)

    @protobug.message
    class BatchGetNoaItemsResponse:
        noaItems: list[NoaItem] = protobug.field(1, default_factory=list)

    @protobug.message
    class Blackout:
        tsInNg: protobug.Int32 | None = protobug.field(1, default=None)
        tsplusInNg: protobug.Int32 | None = protobug.field(2, default=None)
        tsOutNg: protobug.Int32 | None = protobug.field(3, default=None)
        tsplusOutNg: protobug.Int32 | None = protobug.field(4, default=None)
        failedRecord: protobug.Int32 | None = protobug.field(5, default=None)

    @protobug.message
    class BoolValue:
        value: protobug.Bool | None = protobug.field(1, default=None)

    @protobug.message
    class CreateFollowingItemRequest:
        rSeasonId: protobug.String | None = protobug.field(3, default=None)
        stationId: protobug.String | None = protobug.field(4, default=None)
        notifyBefore: protobug.Int32 | None = protobug.field(100, default=None)

    @protobug.message
    class CreateFollowingItemResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreateListenLaterRequest:
        programId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreateListenLaterResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreateNoaItemRequest:
        noaItem: NoaItem | None = protobug.field(1, default=None)

    @protobug.message
    class CreateNoaItemResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreatePlayHistoryRequest:
        programId: protobug.String | None = protobug.field(1, default=None)
        programSource: ProgramSource | None = protobug.field(2, default=None)

    @protobug.message
    class CreatePlayHistoryResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreatePodcastEpisodeBookmarkRequest:
        episodeId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreatePodcastEpisodeBookmarkResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreatePodcastEpisodePlayHistoryRequest:
        episodeId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreatePodcastEpisodePlayHistoryResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreateUserFollowingPodcastChannelRequest:
        channelId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class CreateUserFollowingPodcastChannelResponse:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class DebugInfo:
        stackEntries: protobug.String | None = protobug.field(1, default=None)
        detail: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class DeleteFollowingItemRequest:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class DeleteListenLaterRequest:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class DeleteListenLaterResponse:
        pass

    @protobug.message
    class DeleteNoaItemRequest:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class DeletePodcastEpisodeBookmarkRequest:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class DeleteUserFollowingPodcastChannelRequest:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class Duration:
        seconds: protobug.Int64 | None = protobug.field(1, default=None)
        nanos: protobug.Int32 | None = protobug.field(2, default=None)

    @protobug.message
    class Empty:
        pass

    @protobug.message
    class EpisodeAudio:
        revision: protobug.Int64 | None = protobug.field(1, default=None)
        url: protobug.String | None = protobug.field(2, default=None)
        fileSize: protobug.Int64 | None = protobug.field(3, default=None)
        durationSec: protobug.Int64 | None = protobug.field(4, default=None)
        transcoded: protobug.Int32 | None = protobug.field(5, default=None)

    @protobug.message
    class MetadataEntry:
        pass

    @protobug.message
    class ErrorInfo:
        reason: protobug.String | None = protobug.field(1, default=None)
        domain: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class notify_before:
        duration: Duration | None = protobug.field(1, default=None)

    @protobug.message
    class FollowReminder:
        followingItemId: protobug.String | None = protobug.field(1, default=None)
        stationId: protobug.String | None = protobug.field(3, default=None)
        rSeasonId: protobug.String | None = protobug.field(12, default=None)
        notifyBeforeDuration: notify_before | None = protobug.field(100, default=None)
        notifyMon: protobug.Int32 | None = protobug.field(101, default=None)
        notifyTue: protobug.Int32 | None = protobug.field(102, default=None)
        notifyWed: protobug.Int32 | None = protobug.field(103, default=None)
        notifyThu: protobug.Int32 | None = protobug.field(104, default=None)
        notifyFri: protobug.Int32 | None = protobug.field(105, default=None)
        notifySat: protobug.Int32 | None = protobug.field(106, default=None)
        notifySun: protobug.Int32 | None = protobug.field(107, default=None)

    @protobug.message
    class Genre:
        id: protobug.String | None = protobug.field(1, default=None)
        name: protobug.String | None = protobug.field(2, default=None)
        kind: GenreKind | None = protobug.field(3, default=None)
        userSelected: protobug.Int32 | None = protobug.field(4, default=None)

    @protobug.message
    class GenreActor:
        id: protobug.String | None = protobug.field(1, default=None)
        name: protobug.String | None = protobug.field(2, default=None)
        imageUrl: protobug.String | None = protobug.field(3, default=None)

    @protobug.message
    class GetActorRequest:
        actorKey: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class GetActorResponse:
        actor: Actor | None = protobug.field(1, default=None)

    @protobug.message
    class GetFollowingItemRequest:
        rSeasonId: protobug.String | None = protobug.field(3, default=None)
        orFail: protobug.Int32 | None = protobug.field(100, default=None)

    @protobug.message
    class GetFollowingItemResponse:
        followingItem: FollowingItem | None = protobug.field(1, default=None)

    @protobug.message
    class GetListenLaterRequest:
        programId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class ListenLater:
        id: protobug.String | None = protobug.field(1, default=None)
        programId: protobug.String | None = protobug.field(2, default=None)
        stationId: protobug.String | None = protobug.field(4, default=None)
        createdAt: Timestamp | None = protobug.field(5, default=None)

    @protobug.message
    class GetListenLaterResponse:
        listenLater: ListenLater | None = protobug.field(1, default=None)

    @protobug.message
    class GetPodcastChannelRequest:
        id: protobug.String | None = protobug.field(1, default=None)
        isTimefreePlus: protobug.Int32 | None = protobug.field(2, default=None)

    @protobug.message
    class PodcastChannel:
        id: protobug.String | None = protobug.field(1, default=None)
        workspaceId: protobug.String | None = protobug.field(2, default=None)
        rSeasonIds: protobug.String | None = protobug.field(3, default=None)
        title: protobug.String | None = protobug.field(4, default=None)
        description: protobug.String | None = protobug.field(5, default=None)
        imageUrl: protobug.String | None = protobug.field(6, default=None)
        author: protobug.String | None = protobug.field(11, default=None)
        startAt: Timestamp | None = protobug.field(26, default=None)
        endAt: Timestamp | None = protobug.field(27, default=None)
        episodeCount: protobug.Int64 | None = protobug.field(28, default=None)
        lastStartAt: Timestamp | None = protobug.field(29, default=None)
        isEnabled: protobug.Int32 | None = protobug.field(30, default=None)
        stationName: protobug.String | None = protobug.field(33, default=None)
        thumbnailImageUrl: protobug.String | None = protobug.field(34, default=None)
        stationType: PodcastStationType | None = protobug.field(35, default=None)
        channelUrl: protobug.String | None = protobug.field(36, default=None)
        largeThumbnailImageUrl: protobug.String | None = protobug.field(37, default=None)
        minAge: protobug.Int32 | None = protobug.field(38, default=None)

    @protobug.message
    class GetPodcastChannelResponse:
        channel: PodcastChannel | None = protobug.field(1, default=None)

    @protobug.message
    class GetPodcastEpisodeRequest:
        id: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class PodcastEpisode:
        id: protobug.String | None = protobug.field(1, default=None)
        workspaceId: protobug.String | None = protobug.field(2, default=None)
        channelId: protobug.String | None = protobug.field(3, default=None)
        title: protobug.String | None = protobug.field(4, default=None)
        description: protobug.String | None = protobug.field(5, default=None)
        imageUrl: protobug.String | None = protobug.field(7, default=None)
        audio: EpisodeAudio | None = protobug.field(8, default=None)
        channelImageUrl: protobug.String | None = protobug.field(16, default=None)
        channelTitle: protobug.String | None = protobug.field(17, default=None)
        channelStationName: protobug.String | None = protobug.field(18, default=None)
        channelAuthor: protobug.String | None = protobug.field(19, default=None)
        thumbnailImageUrl: protobug.String | None = protobug.field(20, default=None)
        channelThumbnailImageUrl: protobug.String | None = protobug.field(21, default=None)
        channelStationType: PodcastStationType | None = protobug.field(22, default=None)
        startAt: Timestamp | None = protobug.field(27, default=None)
        endAt: Timestamp | None = protobug.field(28, default=None)
        isEnabled: protobug.Int32 | None = protobug.field(29, default=None)
        hasTranscription: protobug.Int32 | None = protobug.field(32, default=None)
        channelLargeThumbnailImageUrl: protobug.String | None = protobug.field(33, default=None)
        minAge: protobug.Int32 | None = protobug.field(34, default=None)

    @protobug.message
    class GetPodcastEpisodeResponse:
        episode: PodcastEpisode | None = protobug.field(1, default=None)

    @protobug.message
    class GetRSeasonRequest:
        rSeasonId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class ProgramGenre:
        program: Genre | None = protobug.field(1, default=None)
        personality: Genre | None = protobug.field(2, default=None)

    @protobug.message
    class RSeason:
        id: protobug.String | None = protobug.field(1, default=None)
        mindsSeasonId: protobug.String | None = protobug.field(2, default=None)
        rSeasonName: protobug.String | None = protobug.field(3, default=None)
        backgroundImageUrl: protobug.String | None = protobug.field(4, default=None)
        twitterAccountId: protobug.String | None = protobug.field(5, default=None)
        summary: protobug.String | None = protobug.field(6, default=None)
        genre: ProgramGenre | None = protobug.field(7, default=None)
        actorIds: protobug.String | None = protobug.field(8, default=None)
        url: protobug.String | None = protobug.field(9, default=None)
        performer: protobug.String | None = protobug.field(10, default=None)
        backgroundImageSquareUrl: protobug.String | None = protobug.field(11, default=None)

    @protobug.message
    class GetRSeasonResponse:
        rSeason: RSeason | None = protobug.field(1, default=None)

    @protobug.message
    class Link:
        description: protobug.String | None = protobug.field(1, default=None)
        url: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class Help:
        links: list[Link] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListFollowRemindersResponse:
        reminders: list[FollowReminder] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListFollowingItemsRequest:
        lastCreatedAt: Timestamp | None = protobug.field(1, default=None)
        lastDow: TypeDayOfWeek | None = protobug.field(2, default=None)
        lastStartAtTime: protobug.String | None = protobug.field(3, default=None)
        lastUserFollowingItemDowId: protobug.String | None = protobug.field(4, default=None)
        limit: protobug.Int32 | None = protobug.field(50, default=None)
        createdAtSortAscending: protobug.Int32 | None = protobug.field(51, default=None)
        dowSortAscending: protobug.Int32 | None = protobug.field(52, default=None)
        startAtTimeSortAscending: protobug.Int32 | None = protobug.field(53, default=None)
        sortKey: protobug.String | None = protobug.field(100, default=None)

    @protobug.message
    class ListFollowingItemsResponse:
        followingItems: list[FollowingItem] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListListenLatersRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastCreatedAt: Timestamp | None = protobug.field(2, default=None)

    @protobug.message
    class ListListenLatersResponse:
        listenLaters: list[ListenLater] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListNoaItemsRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastCreatedAt: Timestamp | None = protobug.field(2, default=None)

    @protobug.message
    class ListNoaItemsResponse:
        noaItems: list[NoaItem] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPersonalizedPodcastChannelsRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastChannelId: protobug.String | None = protobug.field(2, default=None)
        noCache: protobug.Int32 | None = protobug.field(3, default=None)

    @protobug.message
    class ListPersonalizedPodcastChannelsResponse:
        channels: list[PodcastChannel] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPinpointAccessRequest:
        pass

    @protobug.message
    class PinpointAccessItem:
        type: protobug.String | None = protobug.field(1, default=None)
        id: protobug.String | None = protobug.field(2, default=None)
        isUnplayed: protobug.Int32 | None = protobug.field(3, default=None)
        title: protobug.String | None = protobug.field(4, default=None)
        squareImageUrl: protobug.String | None = protobug.field(5, default=None)
        latestEpisodeIds: protobug.String | None = protobug.field(6, default=None)

    @protobug.message
    class ListPinpointAccessResponse:
        items: list[PinpointAccessItem] = protobug.field(1, default_factory=list)

    @protobug.message
    class Program:
        id: protobug.String | None = protobug.field(1, default=None)
        eventId: protobug.String | None = protobug.field(2, default=None)
        mindsEventId: protobug.String | None = protobug.field(3, default=None)
        mindsSeasonId: protobug.String | None = protobug.field(5, default=None)
        episodeId: protobug.String | None = protobug.field(7, default=None)
        mindsEpisodeId: protobug.String | None = protobug.field(8, default=None)
        title: protobug.String | None = protobug.field(9, default=None)
        broadcastDate: protobug.String | None = protobug.field(10, default=None)
        startAt: Timestamp | None = protobug.field(11, default=None)
        endAt: Timestamp | None = protobug.field(12, default=None)
        summary: protobug.String | None = protobug.field(13, default=None)
        description: protobug.String | None = protobug.field(14, default=None)
        performer: protobug.String | None = protobug.field(15, default=None)
        imageUrl: protobug.String | None = protobug.field(16, default=None)
        url: protobug.String | None = protobug.field(17, default=None)
        genre: ProgramGenre | None = protobug.field(18, default=None)
        tags: protobug.String | None = protobug.field(19, default=None)
        actorIds: protobug.String | None = protobug.field(20, default=None)
        keyStationId: protobug.String | None = protobug.field(21, default=None)
        keyStationName: protobug.String | None = protobug.field(22, default=None)
        stationId: protobug.String | None = protobug.field(23, default=None)
        stationName: protobug.String | None = protobug.field(24, default=None)
        rSeasonId: protobug.String | None = protobug.field(43, default=None)
        rSeasonName: protobug.String | None = protobug.field(44, default=None)
        score: protobug.Fixed32 | None = protobug.field(45, default=None)
        imageSquareUrl: protobug.String | None = protobug.field(46, default=None)
        episodeIntroductionTitle: protobug.String | None = protobug.field(300, default=None)
        episodeIntroductionSummary: protobug.String | None = protobug.field(301, default=None)
        episodeIntroductionDescription: protobug.String | None = protobug.field(302, default=None)
        episodeIntroductionImageUrl: protobug.String | None = protobug.field(303, default=None)
        episodeIntroductionActorIds: protobug.String | None = protobug.field(304, default=None)
        episodeIntroductionTags: protobug.String | None = protobug.field(305, default=None)
        episodeIntroductionPerformer: protobug.String | None = protobug.field(306, default=None)
        episodeIntroductionStartAt: Timestamp | None = protobug.field(307, default=None)
        isSearchEvent: protobug.Int32 | None = protobug.field(400, default=None)
        isSingleStation: protobug.Int32 | None = protobug.field(401, default=None)
        blackout: Blackout | None = protobug.field(500, default=None)

    @protobug.message
    class PlayHistory:
        id: protobug.String | None = protobug.field(1, default=None)
        program: Program | None = protobug.field(3, default=None)
        playedAt: Timestamp | None = protobug.field(7, default=None)

    @protobug.message
    class ListPlayHistoriesNearDeadlineResponse:
        playHistories: list[PlayHistory] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPlayHistoriesNearTimefreeDeadlineResponse:
        playHistories: list[PlayHistory] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPlayHistoriesRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastPlayedAt: Timestamp | None = protobug.field(2, default=None)

    @protobug.message
    class ListPlayHistoriesResponse:
        playHistories: list[PlayHistory] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPodcastCategoriesRequest:
        pass

    @protobug.message
    class PodcastCategory:
        mainCategory: protobug.String | None = protobug.field(1, default=None)
        mainCategoryJa: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class ListPodcastCategoriesResponse:
        categories: list[PodcastCategory] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPodcastChannelPlayHistoriesRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastPlayedAt: Timestamp | None = protobug.field(2, default=None)
        channelIds: protobug.String | None = protobug.field(3, default=None)

    @protobug.message
    class UserPodcastChannelPlayHistory:
        id: protobug.String | None = protobug.field(1, default=None)
        channel: PodcastChannel | None = protobug.field(2, default=None)
        createdAt: Timestamp | None = protobug.field(3, default=None)
        updatedAt: Timestamp | None = protobug.field(4, default=None)
        lastPlayedEpisodeId: protobug.String | None = protobug.field(5, default=None)

    @protobug.message
    class ListPodcastChannelPlayHistoriesResponse:
        histories: list[UserPodcastChannelPlayHistory] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPodcastChannelsRequest:
        mainCategory: protobug.String | None = protobug.field(1, default=None)
        rSeasonId: protobug.String | None = protobug.field(2, default=None)
        limit: protobug.Int32 | None = protobug.field(3, default=None)
        lastChannelId: protobug.String | None = protobug.field(4, default=None)
        stationId: protobug.String | None = protobug.field(5, default=None)

    @protobug.message
    class ListPodcastChannelsResponse:
        channels: list[PodcastChannel] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPodcastEpisodeBookmarksRequest:
        lastCreatedAt: Timestamp | None = protobug.field(1, default=None)
        limit: protobug.Int32 | None = protobug.field(50, default=None)

    @protobug.message
    class UserPodcastEpisodeBookmark:
        id: protobug.String | None = protobug.field(1, default=None)
        episode: PodcastEpisode | None = protobug.field(2, default=None)
        createdAt: Timestamp | None = protobug.field(3, default=None)
        updatedAt: Timestamp | None = protobug.field(4, default=None)

    @protobug.message
    class ListPodcastEpisodeBookmarksResponse:
        bookmarks: list[UserPodcastEpisodeBookmark] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPodcastEpisodePlayHistoriesRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastPlayedAt: Timestamp | None = protobug.field(2, default=None)

    @protobug.message
    class UserPodcastEpisodePlayHistory:
        id: protobug.String | None = protobug.field(1, default=None)
        episode: PodcastEpisode | None = protobug.field(2, default=None)
        createdAt: Timestamp | None = protobug.field(3, default=None)
        updatedAt: Timestamp | None = protobug.field(4, default=None)

    @protobug.message
    class ListPodcastEpisodePlayHistoriesResponse:
        histories: list[UserPodcastEpisodePlayHistory] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPodcastEpisodesRequest:
        channelId: protobug.String | None = protobug.field(1, default=None)
        order: EpisodeOrder | None = protobug.field(2, default=None)
        playbackStatus: EpisodePlaybackStatusFilter | None = protobug.field(3, default=None)
        limit: protobug.Int32 | None = protobug.field(4, default=None)
        lastEpisodeId: protobug.String | None = protobug.field(5, default=None)

    @protobug.message
    class ListPodcastEpisodesResponse:
        episodes: list[PodcastEpisode] = protobug.field(1, default_factory=list)
        hasNextPage: protobug.Int32 | None = protobug.field(2, default=None)

    @protobug.message
    class ListPodcastStationsRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)

    @protobug.message
    class PodcastStation:
        id: protobug.String | None = protobug.field(1, default=None)
        name: protobug.String | None = protobug.field(2, default=None)
        imageUrl: protobug.String | None = protobug.field(3, default=None)
        ruby: protobug.String | None = protobug.field(4, default=None)

    @protobug.message
    class ListPodcastStationsResponse:
        stations: list[PodcastStation] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPopularActorsRequest:
        genreIds: protobug.String | None = protobug.field(1, default=None)
        timefreeDays: protobug.Int32 | None = protobug.field(2, default=None)
        currentPrefecture: protobug.String | None = protobug.field(3, default=None)
        areafree: protobug.Int32 | None = protobug.field(4, default=None)

    @protobug.message
    class ListPopularActorsResponse:
        genreActors: list[GenreActor] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListPopularPodcastChannelsRequest:
        pass

    @protobug.message
    class ListPopularPodcastChannelsResponse:
        channels: list[PodcastChannel] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListRecommendedPodcastChannelsRequest:
        limit: protobug.Int32 | None = protobug.field(1, default=None)
        lastChannelId: protobug.String | None = protobug.field(2, default=None)
        noCache: protobug.Int32 | None = protobug.field(3, default=None)

    @protobug.message
    class ListRecommendedPodcastChannelsResponse:
        channels: list[PodcastChannel] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListRecommendedProgramsRequest:
        prefecture: protobug.String | None = protobug.field(1, default=None)
        lastRSeasonIdWithAccess: protobug.String | None = protobug.field(100, default=None)
        lastRSeasonIdWithoutAccess: protobug.String | None = protobug.field(101, default=None)
        limit: protobug.Int32 | None = protobug.field(300, default=None)

    @protobug.message
    class ListRecommendedProgramsResponse:
        programs: list[Program] = protobug.field(1, default_factory=list)
        hasNextPage: protobug.Int32 | None = protobug.field(100, default=None)
        lastRSeasonIdWithAccess: protobug.String | None = protobug.field(101, default=None)
        lastRSeasonIdWithoutAccess: protobug.String | None = protobug.field(102, default=None)

    @protobug.message
    class ListRecommendedTagsRequest:
        batchId: protobug.Int32 | None = protobug.field(1, default=None)
        limit: protobug.Int32 | None = protobug.field(2, default=None)
        lastOrderIndex: protobug.Int32 | None = protobug.field(3, default=None)

    @protobug.message
    class RecommendedTag:
        batchId: protobug.Int32 | None = protobug.field(1, default=None)
        tag: protobug.String | None = protobug.field(2, default=None)
        orderIndex: protobug.Int32 | None = protobug.field(3, default=None)

    @protobug.message
    class ListRecommendedTagsResponse:
        tags: list[RecommendedTag] = protobug.field(1, default_factory=list)

    @protobug.message
    class ListRelatedProgramsRequest:
        prefecture: protobug.String | None = protobug.field(1, default=None)
        rSeasonId: protobug.String | None = protobug.field(6, default=None)
        lastRSeasonIdWithAccess: protobug.String | None = protobug.field(100, default=None)
        lastRSeasonIdWithoutAccess: protobug.String | None = protobug.field(101, default=None)
        limit: protobug.Int32 | None = protobug.field(300, default=None)

    @protobug.message
    class ListRelatedProgramsResponse:
        programs: list[Program] = protobug.field(1, default_factory=list)
        hasNextPage: protobug.Int32 | None = protobug.field(100, default=None)
        lastRSeasonIdWithAccess: protobug.String | None = protobug.field(101, default=None)
        lastRSeasonIdWithoutAccess: protobug.String | None = protobug.field(102, default=None)

    @protobug.message
    class ListUserFollowingPodcastChannelsRequest:
        lastCreatedAt: Timestamp | None = protobug.field(1, default=None)
        channelIds: protobug.String | None = protobug.field(2, default=None)
        limit: protobug.Int32 | None = protobug.field(50, default=None)

    @protobug.message
    class UserFollowingPodcastChannel:
        id: protobug.String | None = protobug.field(1, default=None)
        channel: PodcastChannel | None = protobug.field(2, default=None)
        notify: protobug.Int32 | None = protobug.field(3, default=None)
        createdAt: Timestamp | None = protobug.field(4, default=None)
        updatedAt: Timestamp | None = protobug.field(5, default=None)

    @protobug.message
    class ListUserFollowingPodcastChannelsResponse:
        follows: list[UserFollowingPodcastChannel] = protobug.field(1, default_factory=list)

    @protobug.message
    class LocalizedMessage:
        locale: protobug.String | None = protobug.field(1, default=None)
        message: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class Violation:
        type: protobug.String | None = protobug.field(1, default=None)
        subject: protobug.String | None = protobug.field(2, default=None)
        description: protobug.String | None = protobug.field(3, default=None)

    @protobug.message
    class PreconditionFailure:
        violations: list[Violation] = protobug.field(1, default_factory=list)

    @protobug.message
    class ProtoVersion:
        annexProtoVersion: protobug.Int32 | None = protobug.field(1, default=None)

    @protobug.message
    class Violation:
        subject: protobug.String | None = protobug.field(1, default=None)
        description: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class QuotaFailure:
        violations: list[Violation] = protobug.field(1, default_factory=list)

    @protobug.message
    class RequestInfo:
        requestId: protobug.String | None = protobug.field(1, default=None)
        servingData: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class ResourceInfo:
        resourceType: protobug.String | None = protobug.field(1, default=None)
        resourceName: protobug.String | None = protobug.field(2, default=None)
        owner: protobug.String | None = protobug.field(3, default=None)
        description: protobug.String | None = protobug.field(4, default=None)

    @protobug.message
    class RetryInfo:
        retryDelay: Duration | None = protobug.field(1, default=None)

    @protobug.message
    class SaveFollowRemindersRequest:
        reminders: list[FollowReminder] = protobug.field(1, default_factory=list)

    @protobug.message
    class SaveUserFollowingPodcastChannelRemindersRequest:
        id: protobug.String | None = protobug.field(1, default=None)
        notify: protobug.Int32 | None = protobug.field(2, default=None)

    @protobug.message
    class SearchActorsRequest:
        actorName: protobug.String | None = protobug.field(1, default=None)
        from_: protobug.Int32 | None = protobug.field(2, default=None)
        limit: protobug.Int32 | None = protobug.field(3, default=None)

    @protobug.message
    class SearchActorsResponse:
        actors: list[Actor] = protobug.field(1, default_factory=list)
        resultCount: protobug.Int32 | None = protobug.field(2, default=None)
        from_: protobug.Int32 | None = protobug.field(3, default=None)
        totalCount: protobug.Int32 | None = protobug.field(4, default=None)

    @protobug.message
    class SearchArticlesRequest:
        keyword: protobug.String | None = protobug.field(1, default=None)
        actorKey: protobug.String | None = protobug.field(2, default=None)
        rSeasonKey: protobug.String | None = protobug.field(6, default=None)
        seasonKey: protobug.String | None = protobug.field(7, default=None)
        from_: protobug.Int32 | None = protobug.field(100, default=None)
        limit: protobug.Int32 | None = protobug.field(101, default=None)

    @protobug.message
    class SearchArticlesResponse:
        articles: list[Article] = protobug.field(1, default_factory=list)
        resultCount: protobug.Int32 | None = protobug.field(2, default=None)
        from_: protobug.Int32 | None = protobug.field(3, default=None)
        totalCount: protobug.Int32 | None = protobug.field(4, default=None)

    @protobug.message
    class SearchEpisodeStationsRequest:
        episodeId: protobug.String | None = protobug.field(1, default=None)
        programId: protobug.String | None = protobug.field(2, default=None)
        startAtLt: Timestamp | None = protobug.field(8, default=None)
        timefreeDays: protobug.Int32 | None = protobug.field(10, default=None)
        currentPrefecture: protobug.String | None = protobug.field(11, default=None)
        withImplicitBlackoutFilter: protobug.Int32 | None = protobug.field(100, default=None)
        noCache: protobug.Int32 | None = protobug.field(500, default=None)

    @protobug.message
    class SearchStationsResult:
        stationId: protobug.String | None = protobug.field(1, default=None)
        blackout: Blackout | None = protobug.field(2, default=None)
        relatedProgramId: protobug.String | None = protobug.field(3, default=None)
        relatedProgramStartAt: Timestamp | None = protobug.field(4, default=None)

    @protobug.message
    class SearchEpisodeStationsResponse:
        stations: list[SearchStationsResult] = protobug.field(1, default_factory=list)

    @protobug.message
    class SearchProgramsRequest:
        prefecture: protobug.String | None = protobug.field(2, default=None)
        broadcastDate: protobug.String | None = protobug.field(3, default=None)
        genres: protobug.String | None = protobug.field(4, default=None)
        performers: protobug.String | None = protobug.field(5, default=None)
        stationId: protobug.String | None = protobug.field(6, default=None)
        episodeId: protobug.String | None = protobug.field(8, default=None)
        actorId: protobug.String | None = protobug.field(9, default=None)
        isSearchEvent: BoolValue | None = protobug.field(10, default=None)
        startAtLte: Timestamp | None = protobug.field(16, default=None)
        startAtGt: Timestamp | None = protobug.field(17, default=None)
        rSeasonId: protobug.String | None = protobug.field(19, default=None)
        tag: protobug.String | None = protobug.field(20, default=None)
        startAtLt: Timestamp | None = protobug.field(21, default=None)
        startAtGte: Timestamp | None = protobug.field(22, default=None)
        sortKey: protobug.String | None = protobug.field(23, default=None)
        timefreeDays: protobug.Int32 | None = protobug.field(24, default=None)
        currentPrefecture: protobug.String | None = protobug.field(25, default=None)
        limit: protobug.Int32 | None = protobug.field(102, default=None)
        lastStartAt: Timestamp | None = protobug.field(103, default=None)
        lastEventId: protobug.String | None = protobug.field(104, default=None)
        lastScore: protobug.Int32 | None = protobug.field(105, default=None)
        lastIntroductionStartAt: Timestamp | None = protobug.field(106, default=None)
        startAtSortAscending: protobug.Int32 | None = protobug.field(200, default=None)
        noCache: protobug.Int32 | None = protobug.field(500, default=None)

    @protobug.message
    class SearchProgramsResponse:
        programs: list[Program] = protobug.field(1, default_factory=list)

    @protobug.message
    class SearchProgramsWithExplicitKeysRequest:
        keywords: protobug.String | None = protobug.field(1, default=None)
        prefecture: protobug.String | None = protobug.field(2, default=None)
        broadcastDate: protobug.String | None = protobug.field(3, default=None)
        genres: protobug.String | None = protobug.field(4, default=None)
        performers: protobug.String | None = protobug.field(5, default=None)
        stationId: protobug.String | None = protobug.field(6, default=None)
        episodeId: protobug.String | None = protobug.field(8, default=None)
        actorId: protobug.String | None = protobug.field(9, default=None)
        startAtLte: Timestamp | None = protobug.field(16, default=None)
        startAtGt: Timestamp | None = protobug.field(17, default=None)
        rSeasonId: protobug.String | None = protobug.field(19, default=None)
        tag: protobug.String | None = protobug.field(20, default=None)
        endAtGt: Timestamp | None = protobug.field(21, default=None)
        startAtLt: Timestamp | None = protobug.field(22, default=None)
        startAtGte: Timestamp | None = protobug.field(23, default=None)
        isSearchEvent: BoolValue | None = protobug.field(24, default=None)
        sortKey: protobug.String | None = protobug.field(100, default=None)
        ascending: protobug.Int32 | None = protobug.field(101, default=None)
        limit: protobug.Int32 | None = protobug.field(102, default=None)
        lastStartAt: Timestamp | None = protobug.field(103, default=None)
        lastEventId: protobug.String | None = protobug.field(104, default=None)
        lastIntroductionStartAt: Timestamp | None = protobug.field(105, default=None)
        noCache: protobug.Int32 | None = protobug.field(500, default=None)

    @protobug.message
    class SearchProgramsWithExplicitKeysResponse:
        programs: list[Program] = protobug.field(1, default_factory=list)

    @protobug.message
    class SearchStationsByIDRequest:
        rSeasonId: protobug.String | None = protobug.field(5, default=None)
        episodeId: protobug.String | None = protobug.field(6, default=None)
        timefreeDays: protobug.Int32 | None = protobug.field(7, default=None)
        currentPrefecture: protobug.String | None = protobug.field(8, default=None)
        withImplicitBlackoutFilter: protobug.Int32 | None = protobug.field(100, default=None)
        noCache: protobug.Int32 | None = protobug.field(500, default=None)

    @protobug.message
    class SearchStationsByIDResponse:
        stations: list[SearchStationsResult] = protobug.field(1, default_factory=list)

    @protobug.message
    class RSeasonWithStation:
        stationId: protobug.String | None = protobug.field(2, default=None)
        rSeasonId: protobug.String | None = protobug.field(3, default=None)

    @protobug.message
    class SearchUpcomingProgramsByRSeasonIDsRequest:
        dow: list[TypeDayOfWeek] = protobug.field(2, default_factory=list)
        rSeasons: list[RSeasonWithStation] = protobug.field(4, default_factory=list)
        currentPrefecture: protobug.String | None = protobug.field(5, default=None)
        noCache: protobug.Int32 | None = protobug.field(500, default=None)

    @protobug.message
    class SearchUpcomingProgramsByRSeasonIDsResponse:
        programs: list[Program] = protobug.field(1, default_factory=list)

    @protobug.message
    class SignInRequest:
        memberId: protobug.String | None = protobug.field(1, default=None)
        dataId: protobug.String | None = protobug.field(2, default=None)
        prefecture: protobug.String | None = protobug.field(3, default=None)
        oidcAccessToken: protobug.String | None = protobug.field(4, default=None)
        radikoId: protobug.String | None = protobug.field(5, default=None)

    @protobug.message
    class SignInResponse:
        jwtToken: protobug.String | None = protobug.field(1, default=None)
        mainDataId: protobug.String | None = protobug.field(2, default=None)

    @protobug.message
    class SignUpRequest:
        dataId: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class StationImage:
        width: protobug.String | None = protobug.field(1, default=None)
        height: protobug.String | None = protobug.field(2, default=None)
        align: protobug.String | None = protobug.field(3, default=None)
        url: protobug.String | None = protobug.field(4, default=None)

    @protobug.message
    class Station:
        id: protobug.String | None = protobug.field(1, default=None)
        name: protobug.String | None = protobug.field(2, default=None)
        areafree: protobug.String | None = protobug.field(3, default=None)
        timefree: protobug.String | None = protobug.field(4, default=None)
        prefectures: protobug.String | None = protobug.field(5, default=None)
        stationImages: list[StationImage] = protobug.field(6, default_factory=list)
        ruby: protobug.String | None = protobug.field(7, default=None)

    @protobug.message
    class Status:
        code: protobug.Int32 | None = protobug.field(1, default=None)
        message: protobug.String | None = protobug.field(2, default=None)
        details: list[Any] = protobug.field(3, default_factory=list)

    @protobug.message
    class SyncSubscriptionRequest:
        fcmToken: protobug.String | None = protobug.field(1, default=None)

    @protobug.message
    class UpdateFollowingItemRequest:
        id: protobug.String | None = protobug.field(1, default=None)
        notifyBefore: protobug.Int32 | None = protobug.field(2, default=None)
        stationId: protobug.String | None = protobug.field(3, default=None)

    @protobug.message
    class UpdateMemberIDRequest:
        oldMemberId: protobug.String | None = protobug.field(1, default=None)
        memberId: protobug.String | None = protobug.field(2, default=None)
        oidcAccessToken: protobug.String | None = protobug.field(3, default=None)

    @protobug.message
    class UpdateMemberIDResponse:
        jwtToken: protobug.String | None = protobug.field(1, default=None)
