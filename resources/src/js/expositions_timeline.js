import { DataSet, Timeline } from "vis-timeline/standalone";
import { openModal } from "./components/c11_modal";

function applyCategoriesFilters(timeline) {
  var timelineCategoriesList = document.getElementById(
    `timeline_categories_list_filters_${timeline.dom.container.dataset.timelineId}`
  );
  var timelineSortBySelect = document.getElementById(
    `timeline_sort_by_select_${timeline.dom.container.dataset.timelineId}`
  );
  var categoriesFilterCheckedNames = getCategoriesFilterChecked(
    timelineCategoriesList
  ).map(category => {
    return category.id;
  });
  if (timelineSortBySelect.value === "categories") {
    timeline.setGroups(
      new DataSet(getCategoriesFilterChecked(timelineCategoriesList))
    );
    timeline.setItems(
      new DataSet(
        getTimelineItems(
          timeline.dom.container.dataset.milestonesScriptId,
          true,
          categoriesFilterCheckedNames
        )
      )
    );
  }

  if (timelineSortBySelect.value === "dates") {
    let milestonesScriptId = timeline.dom.container.dataset.milestonesScriptId;
    const milestones = JSON.parse(
      document.getElementById(milestonesScriptId).textContent
    );
    let groups = [];
    milestones.forEach(milestone => {
      groups.push({ id: milestone.id });
    });

    timeline.setGroups(new DataSet(groups));
    timeline.setItems(
      new DataSet(
        getTimelineItems(
          timeline.dom.container.dataset.milestonesScriptId,
          false,
          categoriesFilterCheckedNames
        )
      )
    );
  }
}

function moveTimeline(timeline, percentage) {
  var range = timeline.getWindow();
  var interval = range.end - range.start;

  timeline.setWindow({
    start: range.start.valueOf() - interval * percentage,
    end: range.end.valueOf() - interval * percentage
  });
}

function getMilestoneCategoriesClass() {
  return {
    category_blue: "ag-is-timeline__theme-blue",
    category_magenta: "ag-is-timeline__theme-magenta",
    category_green: "ag-is-timeline__theme-green",
    category_purple: "ag-is-timeline__theme-purple",
    category_yellow: "ag-is-timeline__theme-yellow",
    category_red: "ag-is-timeline__theme-red"
  };
}

function getCategoriesFilterChecked(list) {
  const categoriesFilters = list.querySelectorAll(
    `input[name="category"]:checked`
  );
  let groups = [];
  categoriesFilters.forEach(filter => {
    groups.push({ id: filter.value });
  });

  return groups;
}

function getMilestoneCategoryDescription(milestone) {
  // Get milestone categories
  const categoriesScriptId = document.querySelector(
    `#timeline_${milestone.timeline_id}`
  ).dataset.categoriesScriptId;

  return getAllTimelineCategories(categoriesScriptId)[milestone.category];
}

function getAllTimelineCategories(categoriesScriptId) {
  return JSON.parse(document.getElementById(categoriesScriptId).textContent);
}

function getAllTimelineGroups(categoriesScriptId, milestonesScriptId) {
  const groupDataset = [];
  for (const category in getAllTimelineCategories(categoriesScriptId)) {
    groupDataset.push({
      id: category
    });
  }
  const milestones = JSON.parse(
    document.getElementById(milestonesScriptId).textContent
  );
  milestones.forEach(milestone => {
    groupDataset.push({ id: milestone.id });
  });
  return groupDataset;
}

function getContentTemplate(milestone) {
  // Get content template
  let contentTemplate = document
    .getElementById("exposition_timeline_content")
    .content.cloneNode(true).firstElementChild;

  // Set or remove content imagen
  contentTemplate
    .getElementsByClassName("ag-js-timelineContentImage")
    .forEach(imageElement => {
      if (!milestone.image_id) {
        imageElement.remove();
        return;
      }
      if (milestone.is_avatar) {
        imageElement.classList.add("ag-is-timeline_avatar");
      }
      const image = document
        .getElementById(`milestone_image_${milestone.id}`)
        .firstElementChild.cloneNode(true);
      imageElement.querySelectorAll("figure").forEach(figure => {
        figure.appendChild(image);
      });
    });

  // Set content color
  contentTemplate.classList.add(
    getMilestoneCategoriesClass()[milestone.category]
  );

  // Set replacement texts
  const replacement = {
    __title__: milestone.title,
    __firstSubtitle__: milestone.subtitle_1,
    __secondSubtitle__: milestone.subtitle_2,
    __start_year__: getDateYear(milestone.start_date), // procesar
    __end_year__: getDateYear(milestone.end_date) // procesar
  };

  // Replace content left text
  contentTemplate.innerHTML = contentTemplate.innerHTML.replace(
    /__title__|__firstSubtitle__|__secondSubtitle__|__start_year__|__end_year__/gi,
    function(matched) {
      return replacement[matched];
    }
  );
  if (!milestone.subtitle_1) {
    removeContentElement(contentTemplate, "ag-js-firstSubtitle");
  }
  if (!milestone.subtitle_2) {
    removeContentElement(contentTemplate, "ag-js-secondSubtitle");
  }
  if (
    !milestone.end_date ||
    starYearEqualsEndYear(milestone.start_date, milestone.end_date)
  ) {
    removeContentElement(contentTemplate, "ag-js-endYear");
  }

  return contentTemplate;
}

function removeContentElement(contentTemplate, className) {
  contentTemplate.getElementsByClassName(className).forEach(element => {
    element.remove();
  });
}

function getDateYear(date) {
  const fullDateObj = new Date(date);
  return fullDateObj.getFullYear();
}

function starYearEqualsEndYear(startDate, endDate) {
  return getDateYear(startDate) === getDateYear(endDate);
}

function getTimelineItems(
  milestonesScriptId,
  grouped = true,
  categoriesFilter = null
) {
  const milestones = JSON.parse(
    document.getElementById(milestonesScriptId).textContent
  );

  const itemsDataset = [];
  milestones.forEach(milestone => {
    const content = getContentTemplate(milestone);

    let milestone_group = milestone.category;
    if (!grouped) {
      milestone_group = milestone.id;
    }
    if (categoriesFilter && !categoriesFilter.includes(milestone.category)) {
      return;
    }
    const item = {
      id: `timeline_milestone_${milestone.id}`,
      content: content,
      start: milestone.start_date,
      group: milestone_group,
      date_order: milestone.group_order,
      type: "point",
      className: "ag-is-timeline__item",
      autoResize: true,
      modal: `modal-timeline_milestone_${milestone.id}`
    };
    if (milestone.end_date) {
      item.end = milestone.end_date;
      item.type = "range";
    }
    itemsDataset.push(item);
  });
  return itemsDataset;
}

function getOptions() {
  const options = {
    editable: false,
    zoomable: true,
    locale: "es",
    showCurrentTime: false,
    orientation: "top",
    width: "100%",
    margin: { item: 20 },
    dataAttributes: ["modal"],
    zoomKey: "ctrlKey",
    groupOrder: "date_order"
  };

  return options;
}

function renderTimeline(timelineContainer) {
  const groups = new DataSet(
    getAllTimelineGroups(
      timelineContainer.dataset.categoriesScriptId,
      timelineContainer.dataset.milestonesScriptId
    )
  );
  const items = new DataSet(
    getTimelineItems(timelineContainer.dataset.milestonesScriptId)
  );

  return new Timeline(timelineContainer, items, groups, getOptions());
}

function handleFilters(timeline) {
  applyCategoriesFilters(timeline);

  var timelineCategoriesList = document.getElementById(
    `timeline_categories_list_filters_${timeline.dom.container.dataset.timelineId}`
  );
  timelineCategoriesList.addEventListener("change", () => {
    applyCategoriesFilters(timeline);
  });
  var timelineSortBySelect = document.getElementById(
    `timeline_sort_by_select_${timeline.dom.container.dataset.timelineId}`
  );
  timelineSortBySelect.addEventListener("change", () => {
    applyCategoriesFilters(timeline);
  });
}

function handleWindowScrollEvent(timeline) {
  const timelineWrapper = timeline.dom.container.parentElement;
  const timelineSection = timelineWrapper.closest(
    ".ag-js-expositionTimelineSection"
  );
  const filterBtn = timelineWrapper.querySelector(
    `#timeline_filter_button_${timeline.dom.container.dataset.timelineId}`
  );
  const filterAside = timelineWrapper.querySelector(
    `#timeline_filter_aside_${timeline.dom.container.dataset.timelineId}`
  );
  const timelineControls = timelineWrapper.querySelector(
    `#timeline_controls_${timeline.dom.container.dataset.timelineId}`
  );
  const timelineContainer = timeline.dom.container;
  const timeAxis = timeline.dom.top;

  const headerHeight = document.querySelector("header").offsetHeight;
  const windowYOffset = window.pageYOffset + headerHeight;
  const timelineHeaderHeight =
    timelineContainer.offsetTop - timelineSection.offsetTop;
  const timelineHeaderAndContentYOffset =
    timelineSection.offsetTop +
    timelineHeaderHeight +
    timelineContainer.offsetHeight -
    timeAxis.offsetHeight;
  const timelineSectionYOffset =
    timelineSection.offsetTop + timelineSection.offsetHeight;

  if (windowYOffset >= timelineSection.offsetTop) {
    timelineControls.classList.add("ag-is-timeline__control_fix");
    filterBtn.classList.remove("ag-has-button-scroll-down-hidden");
  }
  if (windowYOffset >= timelineContainer.offsetTop) {
    timeAxis.classList.add("ag-is-timeline__fixed-axis");
  }
  if (
    windowYOffset < timelineContainer.offsetTop ||
    windowYOffset > timelineHeaderAndContentYOffset
  ) {
    timeAxis.classList.remove("ag-is-timeline__fixed-axis");
  }
  if (
    windowYOffset < timelineSection.offsetTop ||
    windowYOffset > timelineSectionYOffset
  ) {
    filterBtn.classList.add("ag-has-button-scroll-down-hidden");
    filterAside.classList.add("ag-is-filter-aside-close");
    timelineControls.classList.remove("ag-is-timeline__control_fix");
  }
}

function handleScroll(timeline) {
  handleWindowScrollEvent(timeline);
  window.addEventListener("scroll", function() {
    handleWindowScrollEvent(timeline);
  });
}

function handleFiltersButtons(timeline) {
  const timelineWrapper = timeline.dom.container.parentElement;
  const filterBtn = timelineWrapper.querySelector(
    `#timeline_filter_button_${timeline.dom.container.dataset.timelineId}`
  );
  const filterAside = timelineWrapper.querySelector(
    `#timeline_filter_aside_${timeline.dom.container.dataset.timelineId}`
  );

  filterBtn.addEventListener("click", () => {
    filterAside.classList.toggle("ag-is-filter-aside-close");
    if (!filterAside.classList.contains("ag-is-filter-aside-close")) {
      document
        .getElementsByClassName("ag-js-asideMenuNav")
        .forEach(asideMenu => {
          asideMenu.classList.add("ag-is-menu-aside-close");
        });
    }
  });

  filterAside
    .getElementsByClassName("ag-c-filter-aside__btn-close")
    .forEach(btn => {
      btn.addEventListener("click", function() {
        filterAside.classList.add("ag-is-filter-aside-close");
      });
    });
}

function handleModals(timeline) {
  timeline.on("click", function(properties) {
    if (properties.item) {
      let target =
        this.itemSet.items[properties.item].dom.box ||
        this.itemSet.items[properties.item].dom.point;
      openModal(target);
    }
  });
}

function handleNavigation(timeline) {
  document
    .getElementById(
      `timeline_zoom_in_button_${timeline.dom.container.dataset.timelineId}`
    )
    .addEventListener("click", () => {
      timeline.zoomIn(0.1);
    });

  document
    .getElementById(
      `timeline_zoom_out_button_${timeline.dom.container.dataset.timelineId}`
    )
    .addEventListener("click", () => {
      timeline.zoomOut(0.1);
    });

  document
    .getElementById(
      `timeline_move_right_button_${timeline.dom.container.dataset.timelineId}`
    )
    .addEventListener("click", () => {
      moveTimeline(timeline, 0.2);
    });

  document
    .getElementById(
      `timeline_move_left_button_${timeline.dom.container.dataset.timelineId}`
    )
    .addEventListener("click", () => {
      moveTimeline(timeline, -0.2);
    });
}

document
  .getElementsByClassName("ag-js-expositionTimelineWrapper")
  .forEach(timelineWrapper => {
    const timelineContainer = timelineWrapper.querySelector(
      `#${timelineWrapper.dataset.timelineId}`
    );
    const timeline = renderTimeline(timelineContainer);
    handleFilters(timeline);
    handleScroll(timeline);
    handleFiltersButtons(timeline);
    handleModals(timeline);
    handleNavigation(timeline);
  });
