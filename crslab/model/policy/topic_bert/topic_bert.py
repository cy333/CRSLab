# @Time   : 2020/12/17
# @Author : Yuanhang Zhou
# @Email  : sdzyh002@gmail

# UPDATE
# @Time   : 2021/1/7, 2021/1/4
# @Author : Xiaolei Wang, Yuanhang Zhou
# @email  : wxl1999@foxmail.com, sdzyh002@gmail.com

import os

from torch import nn
from transformers import BertModel

from crslab.config import PRETRAIN_PATH
from crslab.data import dataset_language_map
from crslab.model.base import BaseModel
from crslab.model.pretrain_models import pretrain_models


class TopicBERTModel(BaseModel):
    """This model was proposed in `Towards topic-guided conversational recommender system`_.

    Attributes:
        topic_class_num: A integer indicating the number of topic.

    .. _Towards topic-guided conversational recommender system:
       https://www.aclweb.org/anthology/2020.coling-main.365/

    """

    def __init__(self, opt, device, vocab, side_data):
        """

        Args:
            opt (dict): A dictionary record the hyper parameters.

            device (torch.device): A variable indicating which device to place the data and model.
            vocab (dict): A dictionary record the vocabulary information.
            side_data (dict): A dictionary record the side data.
        
        """
        self.topic_class_num = vocab['n_topic']
        language = dataset_language_map[opt['dataset']]
        dpath = os.path.join(PRETRAIN_PATH, "bert", language)
        resource = pretrain_models['bert'][language]
        super(TopicBERTModel, self).__init__(opt, device, dpath, resource)

    def build_model(self, *args, **kwargs):
        """build model"""
        self.topic_bert = BertModel.from_pretrained(self.dpath)

        self.bert_hidden_size = self.topic_bert.config.hidden_size
        self.state2topic_id = nn.Linear(self.bert_hidden_size,
                                        self.topic_class_num)

        self.loss = nn.CrossEntropyLoss()

    def guide(self, batch, mode):
        # conv_id, message_id, context, context_mask, topic_path_kw, tp_mask, user_profile, profile_mask, y = batch
        context, context_mask, topic_path_kw, tp_mask, user_profile, profile_mask, y = batch

        topic_rep = self.topic_bert(
            topic_path_kw,
            tp_mask).pooler_output  # (bs, hiddensize)

        topic_scores = self.state2topic_id(topic_rep)

        topic_loss = self.loss(topic_scores, y)

        return topic_loss, topic_scores
