<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet extension-element-prefixes="fn my str"
                version="1.0"
                xmlns:cb="http://www.cbeta.org/ns/1.0"
                xmlns:fn="http://exslt.org/functions"
                xmlns:my="urn:foo"
                xmlns:str="http://exslt.org/strings"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output encoding="UTF-8" method="text" />
  <xsl:strip-space elements="*" />

  <!-- Transform a TEI file into plain text, removing all markup.

       Some markup should not have its content included at
       all. Whitespace is added or removed as needed to make the
       output vaguely readable. -->

  <!-- For the edited/master text, pass BASE_WITNESS_ID. -->
  <xsl:param name="witness_id" />
  <xsl:variable name="witness_ref" select="concat(' #', $witness_id, ' ')" />

  <xsl:template match="cb:div|tei:lg|tei:list|tei:p">
    <xsl:call-template name="add_blank_line" />
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="tei:byline" />

  <xsl:template match="tei:caesura">
    <xsl:text>   </xsl:text>
  </xsl:template>

  <xsl:template match="tei:foreign[@place='foot']" />

  <xsl:template match="cb:docNumber" />

  <xsl:template match="tei:item">
    <xsl:text>   </xsl:text>
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="cb:jhead" />

  <xsl:template match="cb:juan" />

  <xsl:template match="tei:l">
    <xsl:text>   </xsl:text>
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="tei:lb[not(local-name(following-sibling::node()[1])='lb')]">
    <xsl:call-template name="add_blank_line" />
  </xsl:template>

  <xsl:template match="tei:lem">
    <xsl:if test="not(../tei:rdg[contains(concat(' ', @wit, ' '), $witness_ref)])">
      <xsl:apply-templates />
    </xsl:if>
  </xsl:template>

  <xsl:template match="cb:mulu" />

  <xsl:template match="tei:note" />

  <xsl:template match="tei:note[@place = 'inline']">
    <xsl:apply-templates select="node()" />
  </xsl:template>

  <xsl:template match="tei:rdg">
    <xsl:variable name="wit" select="concat(' ', @wit, ' ')" />
    <xsl:if test="contains($wit, $witness_ref)">
      <xsl:apply-templates />
    </xsl:if>
  </xsl:template>

  <xsl:template match="tei:teiHeader" />

  <xsl:template match="tei:body//tei:title" />

  <xsl:template match="text()">
    <xsl:value-of select="normalize-space()" />
  </xsl:template>

  <xsl:template match="cb:t[not(@xml:lang='zh')]" />

  <xsl:template name="add_blank_line">
    <xsl:text>
</xsl:text>
  </xsl:template>
</xsl:stylesheet>
